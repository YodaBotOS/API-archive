CREATE TABLE IF NOT EXISTS predict_genre (
    job_id TEXT NOT NULL PRIMARY KEY,
    hash TEXT NOT NULL,
    expire TIMESTAMPTZ DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS chat (
    job_id TEXT NOT NULL,
    status TEXT NOT NULL,
    expire TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '3 minute'),
    messages TEXT[] NOT NULL,
    custom BOOLEAN DEFAULT FALSE,
    custom_prompt BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (job_id)
);

CREATE TABLE IF NOT EXISTS lyrics (
    q TEXT NOT NULL,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    lyrics TEXT NOT NULL,
    track_img TEXT NOT NULL,
    bg_img TEXT NOT NULL,
    raw_dict TEXT NOT NULL,
    PRIMARY KEY (q, title, artist)
);