const CONFIG = {
    annoCorrente: new Date().getFullYear(),

    getAnno() {
        return this.annoCorrente;
    },

    getAnnoPrecedente() {
        return this.annoCorrente - 1;
    }
};