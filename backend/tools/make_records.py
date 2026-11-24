"""seed/records.json 의 synth 정의로 parquet 기록을 만든다.

실제 PhysioNet 기록을 붙이면 이 도구 대신 fetch/select/convert 가 그 자리를 맡는다.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from synth import Profile, generate  # noqa: E402

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    records = json.loads((DATA / "seed" / "records.json").read_text(encoding="utf-8"))
    (DATA / "records").mkdir(parents=True, exist_ok=True)
    for record in records:
        synth = record.get("synth")
        if not synth:
            continue
        target = DATA / record["file_path"]
        frame = generate(synth["seed"], Profile(**synth["profile"]), record["duration_sec"], record["sample_rate"])
        frame.to_parquet(target, index=False, compression="zstd")
        print(f"wrote {target.name}  rows={len(frame)}  {target.stat().st_size / 1024:.0f} KiB")


if __name__ == "__main__":
    main()
