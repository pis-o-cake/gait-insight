import { formatTime } from "../../lib/format";
import { t } from "../../lib/i18n";
import type { Playback } from "../../hooks/usePlayback";

const SPEEDS = [0.5, 1, 2, 5, 10, 30];

export function PlaybackDock({ playback, duration }: { playback: Playback; duration: number }) {
  return (
    <div className="dock">
      <div className="dock-in">
        <button type="button" className="dock-play" data-playing={playback.playing ? 1 : 0}
          aria-label={t(playback.playing ? "an.pause" : "an.play")} onClick={playback.toggle}>
          {playback.playing ? <PauseIcon /> : <PlayIcon />}
          <span>{t(playback.playing ? "an.pause" : "an.play")}</span>
        </button>
        <button type="button" className="dock-reset" aria-label={t("an.reset")} title={t("an.reset")}
          onClick={playback.reset}>
          <ResetIcon />
        </button>
        <div className="dock-time">
          <b>{formatTime(playback.t, true)}</b>
          <span> / {formatTime(duration)}</span>
        </div>
        <div className="dock-seek">
          <input type="range" className="hud-slider" min={0} max={duration} step={0.05}
            value={playback.t} aria-label="시간 이동"
            onChange={(e) => { playback.stop(); playback.setT(Number(e.target.value)); }} />
        </div>
        <div className="dock-speed" role="group" aria-label={t("an.speed")}>
          {SPEEDS.map((s) => (
            <button key={s} type="button" aria-pressed={playback.speed === s}
              onClick={() => playback.setSpeed(s)}>{s}배</button>
          ))}
        </div>
      </div>
    </div>
  );
}

const PlayIcon = () => <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z" /></svg>;
const PauseIcon = () => <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h4v14H7zM13 5h4v14h-4z" /></svg>;
const ResetIcon = () => <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 5v14M18 6l-9 6 9 6z" /></svg>;
