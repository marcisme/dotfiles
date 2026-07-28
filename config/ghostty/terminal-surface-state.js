function run(argv) {
    const surfaceID = String(argv[0]).toLowerCase();
    const ghostty = Application("Ghostty");

    // Do not wake Ghostty while it is quitting or stopped. Detached sessions
    // must survive that state so restored surfaces can reattach to them.
    if (!ghostty.running()) {
        return "ghostty-not-running";
    }

    const terminals = ghostty.terminals();
    for (let index = 0; index < terminals.length; index += 1) {
        if (String(terminals[index].id()).toLowerCase() === surfaceID) {
            return "surface-present";
        }
    }

    return "surface-absent";
}
