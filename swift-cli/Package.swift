// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "HiandbyeCLI",
    platforms: [
        .macOS(.v13)
    ],
    products: [
        .executable(
            name: "hiandbye-swift",
            targets: ["HiandbyeCLI"]
        )
    ],
    targets: [
        .executableTarget(
            name: "HiandbyeCLI",
            path: "Sources/HiandbyeCLI"
        )
    ]
)
