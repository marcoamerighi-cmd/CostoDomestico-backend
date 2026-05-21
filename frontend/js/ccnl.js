const CCNL = {

    2026: {

        conviventi: {
            DS: 1682.42,
            D: 1612.20,
            CS: 1193.84,
            C: 1123.63,
            BS: 1053.39,
            B: 983.16,
            AS: 958.55,
            A: 908.10
        },

        nonConviventi: {
            DS: 9.97,
            D: 9.57,
            CS: 8.30,
            C: 7.86,
            BS: 7.45,
            B: 7.01,
            AS: 6.76,
            A: 6.51
        }
    }
};


function getAnnoCCNL(annoRichiesto = new Date().getFullYear()) {

    const anni = Object.keys(CCNL)
        .map(Number)
        .sort((a,b)=>a-b);

    if (CCNL[annoRichiesto]) {
        return annoRichiesto;
    }

    const disponibili = anni.filter(
        anno => anno <= annoRichiesto
    );

    return disponibili.length
        ? disponibili[disponibili.length - 1]
        : anni[0];
}


function getPagheConviventi() {

    const anno = getAnnoCCNL();

    return CCNL[anno].conviventi;
}


function getPagheNonConviventi() {

    const anno = getAnnoCCNL();

    return CCNL[anno].nonConviventi;
}