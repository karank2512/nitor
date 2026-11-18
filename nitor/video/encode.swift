// Encode a PNG frame sequence to H.264 .mp4 with Apple's AVFoundation (system
// framework; no ffmpeg, nothing installed). Also: `probe` mode reads the
// encoded file back and writes stills at given seconds for pixel inspection.
//   swift encode.swift encode <framesDir> <count> <fps> <out.mp4>
//   swift encode.swift probe  <in.mp4> <outPrefix> <sec> [<sec> ...]
import AVFoundation
import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

func loadCG(_ path: String) -> CGImage {
    let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: path) as CFURL, nil)!
    return CGImageSourceCreateImageAtIndex(src, 0, nil)!
}

let a = CommandLine.arguments
if a[1] == "encode" {
    let dir = a[2], count = Int(a[3])!, fps = Int32(a[4])!, out = URL(fileURLWithPath: a[5])
    let first = loadCG("\(dir)/f0000.png")
    let w = first.width, h = first.height
    let writer = try! AVAssetWriter(outputURL: out, fileType: .mp4)
    let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
        AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: w, AVVideoHeightKey: h,
        AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: (a.count > 6 ? Int(a[6])! : 10_000_000)]])
    input.expectsMediaDataInRealTime = false
    let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
        kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
        kCVPixelBufferWidthKey as String: w, kCVPixelBufferHeightKey as String: h])
    writer.add(input)
    writer.startWriting()
    writer.startSession(atSourceTime: .zero)
    for i in 0..<count {
        while !input.isReadyForMoreMediaData { usleep(2000) }
        let img = loadCG(String(format: "%@/f%04d.png", dir, i))
        var pb: CVPixelBuffer?
        CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &pb)
        CVPixelBufferLockBaseAddress(pb!, [])
        let ctx = CGContext(data: CVPixelBufferGetBaseAddress(pb!), width: w, height: h, bitsPerComponent: 8,
                            bytesPerRow: CVPixelBufferGetBytesPerRow(pb!), space: CGColorSpaceCreateDeviceRGB(),
                            bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue)!
        ctx.draw(img, in: CGRect(x: 0, y: 0, width: w, height: h))
        CVPixelBufferUnlockBaseAddress(pb!, [])
        adaptor.append(pb!, withPresentationTime: CMTime(value: Int64(i), timescale: fps))
    }
    input.markAsFinished()
    let sem = DispatchSemaphore(value: 0)
    writer.finishWriting { sem.signal() }
    sem.wait()
    print("status", writer.status.rawValue, writer.error as Any)
} else if a[1] == "stats" {
    // decode EVERY frame of the encoded file; per frame: mean luma, max luma,
    // ink fraction (>128), mean abs diff vs previous frame (every 4th px)
    let asset = AVURLAsset(url: URL(fileURLWithPath: a[2]))
    let reader = try! AVAssetReader(asset: asset)
    let track = asset.tracks(withMediaType: .video)[0]
    let out = AVAssetReaderTrackOutput(track: track, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
    reader.add(out); reader.startReading()
    var prev: [UInt8] = []; var lines = ["frame,t,mean,max,ink,diff"]; var k = 0
    while let sb = out.copyNextSampleBuffer() {
        let pb = CMSampleBufferGetImageBuffer(sb)!
        CVPixelBufferLockBaseAddress(pb, .readOnly)
        let w = CVPixelBufferGetWidth(pb), h = CVPixelBufferGetHeight(pb), bpr = CVPixelBufferGetBytesPerRow(pb)
        let base = CVPixelBufferGetBaseAddress(pb)!.assumingMemoryBound(to: UInt8.self)
        var cur: [UInt8] = []; cur.reserveCapacity((w / 4) * (h / 4))
        var sum = 0, mx = 0, ink = 0, dsum = 0
        for y in stride(from: 0, to: h, by: 4) { for x in stride(from: 0, to: w, by: 4) {
            let p = base + y * bpr + x * 4
            let l = (Int(p[2]) * 299 + Int(p[1]) * 587 + Int(p[0]) * 114) / 1000
            cur.append(UInt8(l)); sum += l; mx = max(mx, l); if l > 128 { ink += 1 }
        } }
        if !prev.isEmpty { for i in 0..<cur.count { dsum += abs(Int(cur[i]) - Int(prev[i])) } }
        CVPixelBufferUnlockBaseAddress(pb, .readOnly)
        let n = Double(cur.count), t = CMTimeGetSeconds(CMSampleBufferGetPresentationTimeStamp(sb))
        lines.append(String(format: "%d,%.3f,%.2f,%d,%.5f,%.3f", k, t, Double(sum) / n, mx, Double(ink) / n, prev.isEmpty ? 0 : Double(dsum) / n))
        prev = cur; k += 1
    }
    try! lines.joined(separator: "\n").write(toFile: a[3], atomically: true, encoding: .utf8)
    print("frames", k)
} else {
    let asset = AVURLAsset(url: URL(fileURLWithPath: a[2]))
    let sem = DispatchSemaphore(value: 0)
    Task {
        let dur = try! await asset.load(.duration)
        let tracks = try! await asset.loadTracks(withMediaType: .video)
        let size = try! await tracks[0].load(.naturalSize)
        let audio = try! await asset.loadTracks(withMediaType: .audio)
        print("duration_s", CMTimeGetSeconds(dur), "size", size, "video_tracks", tracks.count, "audio_tracks", audio.count)
        let gen = AVAssetImageGenerator(asset: asset)
        gen.requestedTimeToleranceBefore = .zero
        gen.requestedTimeToleranceAfter = .zero
        for s in a[4...] {
            let (img, _) = try! await gen.image(at: CMTime(seconds: Double(s)!, preferredTimescale: 600))
            let url = URL(fileURLWithPath: "\(a[3])-\(s)s.png")
            let dst = CGImageDestinationCreateWithURL(url as CFURL, UTType.png.identifier as CFString, 1, nil)!
            CGImageDestinationAddImage(dst, img, nil)
            CGImageDestinationFinalize(dst)
            print("still", url.path)
        }
        sem.signal()
    }
    sem.wait()
}
