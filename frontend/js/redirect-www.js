if (window.location.hostname === "www.costodomestico.it") {
    window.location.replace(
        "https://costodomestico.it" +
        window.location.pathname +
        window.location.search +
        window.location.hash
    );
}