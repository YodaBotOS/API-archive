CREATE TABLE IF NOT EXISTS predict_genre (
    job_id TEXT NOT NULL PRIMARY KEY,
    hash TEXT NOT NULL
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