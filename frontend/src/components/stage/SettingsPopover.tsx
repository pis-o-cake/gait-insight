import { useEffect, useRef } from "react";
import { PALETTES } from "../../lib/palette";
import { t } from "../../lib/i18n";
import type { DisplayOptions } from "./HeatmapCanvas";

interface Props {
  open: boolean;
  options: DisplayOptions;
  onChange: (next: DisplayOptions) => void;
  onClose: () => void;
}

export function SettingsPopover({ open, options, onChange, onClose }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) onClose();
    };
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open, onClose]);

  if (!open) return null;

  const toggle = (key: "outline" | "sensors" | "cop") => () =>
    onChange({ ...options, [key]: !options[key] });

  return (
    <div className="stage-pop" ref={ref}>
      <div className="pop-group">
        <span className="lab">{t("an.palette")}</span>
        <div className="pal-list">
          {Object.keys(PALETTES).map((name) => (
            <button key={name} type="button" aria-pressed={options.palette === name}
              onClick={() => onChange({ ...options, palette: name })}>{name}</button>
          ))}
        </div>
      </div>
      <div className="pop-group">
        <label className="lab" htmlFor="cutoff">{t("an.cutoff")}<b>{options.cutoff} N</b></label>
        <input type="range" className="hud-slider" id="cutoff" min={0} max={120} step={5}
          value={options.cutoff} onChange={(e) => onChange({ ...options, cutoff: Number(e.target.value) })} />
      </div>
      <div className="pop-group">
        <label className="switch">{t("an.overlay.outline")}
          <input type="checkbox" checked={options.outline} onChange={toggle("outline")} /></label>
        <label className="switch">{t("an.overlay.sensors")}
          <input type="checkbox" checked={options.sensors} onChange={toggle("sensors")} /></label>
        <label className="switch">{t("an.overlay.cop")}
          <input type="checkbox" checked={options.cop} onChange={toggle("cop")} /></label>
      </div>
    </div>
  );
}
