function run(argv) {
    const markerPath = argv[0];
    const ghostty = Application("Ghostty");
    const terminals = ghostty.terminals();

    for (let index = 0; index < terminals.length; index += 1) {
        if (terminals[index].workingDirectory() === markerPath) {
            return terminals[index].id();
        }
    }

    return "";
}
