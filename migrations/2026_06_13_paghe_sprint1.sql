BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS paghe_famiglie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    nome VARCHAR(100),
    cognome VARCHAR(100),
    telefono VARCHAR(50),
    stato VARCHAR(30) NOT NULL DEFAULT 'attiva',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS paghe_datori (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    famiglia_id UUID NOT NULL REFERENCES paghe_famiglie(id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    cognome VARCHAR(100) NOT NULL,
    codice_fiscale VARCHAR(16),
    email VARCHAR(255),
    telefono VARCHAR(50),
    indirizzo TEXT,
    comune VARCHAR(100),
    provincia VARCHAR(10),
    cap VARCHAR(10),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS paghe_lavoratori (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    famiglia_id UUID NOT NULL REFERENCES paghe_famiglie(id) ON DELETE CASCADE,
    nome VARCHAR(100) NOT NULL,
    cognome VARCHAR(100) NOT NULL,
    codice_fiscale VARCHAR(16),
    data_nascita DATE,
    luogo_nascita VARCHAR(100),
    nazionalita VARCHAR(100),
    email VARCHAR(255),
    telefono VARCHAR(50),
    indirizzo TEXT,
    iban VARCHAR(34),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS paghe_rapporti (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    famiglia_id UUID NOT NULL REFERENCES paghe_famiglie(id) ON DELETE CASCADE,
    datore_id UUID NOT NULL REFERENCES paghe_datori(id) ON DELETE CASCADE,
    lavoratore_id UUID NOT NULL REFERENCES paghe_lavoratori(id) ON DELETE CASCADE,

    tipo_contratto VARCHAR(30) NOT NULL DEFAULT 'tempo_indeterminato',
data_fine_contratto DATE,
motivo_termine VARCHAR(255),
proroghe JSONB,
    mansione VARCHAR(50) NOT NULL,
    livello VARCHAR(10) NOT NULL,
    convivente BOOLEAN NOT NULL DEFAULT FALSE,

    ore_settimanali NUMERIC(6,2) NOT NULL,
    tipo_orario VARCHAR(30) DEFAULT 'part_time',
    part_time_art14 BOOLEAN DEFAULT FALSE,

    paga_oraria NUMERIC(10,2),
    paga_mensile NUMERIC(10,2),
    paga_pattuita_tipo VARCHAR(20),

    data_assunzione DATE NOT NULL,
    data_cessazione DATE,

    stato VARCHAR(30) NOT NULL DEFAULT 'attivo',

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS paghe_variazioni_rapporto (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rapporto_id UUID NOT NULL REFERENCES paghe_rapporti(id) ON DELETE CASCADE,
    data_decorrenza DATE NOT NULL,
    tipo_variazione VARCHAR(50) NOT NULL,
    dati_precedenti JSONB,
    dati_nuovi JSONB,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS paghe_mesi (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rapporto_id UUID NOT NULL REFERENCES paghe_rapporti(id) ON DELETE CASCADE,
    anno INTEGER NOT NULL,
    mese INTEGER NOT NULL,
    stato VARCHAR(30) NOT NULL DEFAULT 'aperto',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (rapporto_id, anno, mese)
);

CREATE TABLE IF NOT EXISTS paghe_eventi (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mese_id UUID NOT NULL REFERENCES paghe_mesi(id) ON DELETE CASCADE,
    rapporto_id UUID NOT NULL REFERENCES paghe_rapporti(id) ON DELETE CASCADE,
    tipo_evento VARCHAR(50) NOT NULL,
    data_inizio DATE NOT NULL,
    data_fine DATE,
    ore NUMERIC(6,2),
    giorni NUMERIC(6,2),
    importo NUMERIC(10,2),
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS paghe_cedolini (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mese_id UUID NOT NULL REFERENCES paghe_mesi(id) ON DELETE CASCADE,
    rapporto_id UUID NOT NULL REFERENCES paghe_rapporti(id) ON DELETE CASCADE,
    numero_cedolino VARCHAR(50),
    lordo NUMERIC(10,2) DEFAULT 0,
    contributi_lavoratore NUMERIC(10,2) DEFAULT 0,
    netto NUMERIC(10,2) DEFAULT 0,
    tfr_maturato NUMERIC(10,2) DEFAULT 0,
    tredicesima_maturata NUMERIC(10,2) DEFAULT 0,
    dati_calcolo JSONB,
    pdf_url TEXT,
    stato VARCHAR(30) NOT NULL DEFAULT 'bozza',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS paghe_documenti (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    famiglia_id UUID NOT NULL REFERENCES paghe_famiglie(id) ON DELETE CASCADE,
    rapporto_id UUID REFERENCES paghe_rapporti(id) ON DELETE SET NULL,
    cedolino_id UUID REFERENCES paghe_cedolini(id) ON DELETE SET NULL,
    tipo_documento VARCHAR(50) NOT NULL,
    nome_file VARCHAR(255),
    url_file TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS paghe_contributi_trimestrali (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rapporto_id UUID NOT NULL REFERENCES paghe_rapporti(id) ON DELETE CASCADE,
    anno INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    ore_retribuite NUMERIC(8,2) DEFAULT 0,
    contributi_totali NUMERIC(10,2) DEFAULT 0,
    contributi_datore NUMERIC(10,2) DEFAULT 0,
    contributi_lavoratore NUMERIC(10,2) DEFAULT 0,
    stato VARCHAR(30) NOT NULL DEFAULT 'da_pagare',
    scadenza DATE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (rapporto_id, anno, trimestre)
);

CREATE TABLE IF NOT EXISTS paghe_tfr (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rapporto_id UUID NOT NULL REFERENCES paghe_rapporti(id) ON DELETE CASCADE,
    anno INTEGER NOT NULL,
    quota_annua NUMERIC(10,2) DEFAULT 0,
    rivalutazione NUMERIC(10,2) DEFAULT 0,
    anticipi NUMERIC(10,2) DEFAULT 0,
    totale_accantonato NUMERIC(10,2) DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (rapporto_id, anno)
);

CREATE TABLE IF NOT EXISTS paghe_tfr_movimenti (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rapporto_id UUID NOT NULL REFERENCES paghe_rapporti(id) ON DELETE CASCADE,
    tipo_movimento VARCHAR(50) NOT NULL,
    data_movimento DATE NOT NULL,
    importo NUMERIC(10,2) NOT NULL,
    note TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS paghe_cu (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rapporto_id UUID NOT NULL REFERENCES paghe_rapporti(id) ON DELETE CASCADE,
    anno INTEGER NOT NULL,
    dati_cu JSONB,
    pdf_url TEXT,
    stato VARCHAR(30) NOT NULL DEFAULT 'bozza',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (rapporto_id, anno)
);

CREATE TABLE IF NOT EXISTS paghe_abbonamenti (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    famiglia_id UUID NOT NULL REFERENCES paghe_famiglie(id) ON DELETE CASCADE,
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    piano VARCHAR(50) NOT NULL,
    stato VARCHAR(30) NOT NULL DEFAULT 'attivo',
    data_inizio DATE NOT NULL DEFAULT CURRENT_DATE,
    data_fine DATE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS paghe_log_attivita (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    famiglia_id UUID REFERENCES paghe_famiglie(id) ON DELETE SET NULL,
    utente_email VARCHAR(255),
    azione VARCHAR(100) NOT NULL,
    descrizione TEXT,
    dati JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_paghe_famiglie_email ON paghe_famiglie(email);
CREATE INDEX IF NOT EXISTS idx_paghe_rapporti_famiglia ON paghe_rapporti(famiglia_id);
CREATE INDEX IF NOT EXISTS idx_paghe_mesi_rapporto ON paghe_mesi(rapporto_id);
CREATE INDEX IF NOT EXISTS idx_paghe_cedolini_rapporto ON paghe_cedolini(rapporto_id);
CREATE INDEX IF NOT EXISTS idx_paghe_eventi_rapporto ON paghe_eventi(rapporto_id);
CREATE INDEX IF NOT EXISTS idx_paghe_log_famiglia ON paghe_log_attivita(famiglia_id);

COMMIT;