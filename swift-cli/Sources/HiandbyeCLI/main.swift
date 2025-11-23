import Foundation

struct Arguments {
    var config: String?
    var engine: String = "whisper"
}

func parseArguments() -> Arguments? {
    var args = Arguments()
    var iterator = CommandLine.arguments.dropFirst().makeIterator()

    while let argument = iterator.next() {
        switch argument {
        case "--config":
            guard let configPath = iterator.next() else { return nil }
            args.config = configPath
        case "--engine":
            guard let engineValue = iterator.next() else { return nil }
            args.engine = engineValue
        default:
            return nil
        }
    }

    return args.config == nil ? nil : args
}

func printUsage() {
    let message = """
    Usage: hiandbye-swift --config <path> [--engine whisper|sr]

    The Swift CLI wraps the Python keyword listener. Ensure Python dependencies are installed.
    """
    print(message)
}

func repoRootFromSource() -> URL? {
    // #file points to .../swift-cli/Sources/HiandbyeCLI/main.swift
    // Walk up to the repository root so we can find keyword_listener.py
    let sourceURL = URL(fileURLWithPath: #file)
    return sourceURL
        .deletingLastPathComponent() // main.swift directory
        .deletingLastPathComponent() // HiandbyeCLI
        .deletingLastPathComponent() // Sources
        .deletingLastPathComponent() // swift-cli
        .deletingLastPathComponent() // repo root
}

func runPythonListener(configPath: String, engine: String) throws {
    guard let repoRoot = repoRootFromSource() else {
        throw RuntimeError("Unable to locate repository root from source path")
    }

    let scriptPath = repoRoot.appendingPathComponent("keyword_listener.py").path
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/usr/bin/env")
    process.arguments = ["python3", scriptPath, "--config", configPath, "--engine", engine]
    process.standardInput = FileHandle.standardInput
    process.standardOutput = FileHandle.standardOutput
    process.standardError = FileHandle.standardError

    try process.run()
    process.waitUntilExit()

    if process.terminationStatus != 0 {
        throw RuntimeError("keyword_listener.py exited with status \(process.terminationStatus)")
    }
}

struct RuntimeError: Error, CustomStringConvertible {
    let message: String
    init(_ message: String) { self.message = message }
    var description: String { message }
}

guard let parsed = parseArguments() else {
    printUsage()
    exit(1)
}

do {
    try runPythonListener(configPath: parsed.config!, engine: parsed.engine)
} catch {
    fputs("\(error)\n", stderr)
    exit(1)
}
