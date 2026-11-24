import { useCallback, useEffect, useRef, useState } from "react";

export interface Playback {
  t: number;
  playing: boolean;
  speed: number;
  setT: (value: number) => void;
  setSpeed: (value: number) => void;
  toggle: () => void;
  reset: () => void;
  stop: () => void;
}

/** 재생 시각 하나를 화면 전체가 공유한다. 히트맵·그래프·시크바가 같은 t 를 읽는다. */
export function usePlayback(duration: number): Playback {
  const [t, setT] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const frame = useRef(0);
  const last = useRef(0);

  const stop = useCallback(() => {
    setPlaying(false);
    if (frame.current) cancelAnimationFrame(frame.current);
    frame.current = 0;
  }, []);

  useEffect(() => {
    if (!playing) return;
    last.current = performance.now();
    const tick = (now: number) => {
      const delta = ((now - last.current) / 1000) * speed;
      last.current = now;
      setT((prev) => {
        const next = prev + delta;
        if (next >= duration) {
          setPlaying(false);
          return duration;
        }
        return next;
      });
      frame.current = requestAnimationFrame(tick);
    };
    frame.current = requestAnimationFrame(tick);
    return () => {
      if (frame.current) cancelAnimationFrame(frame.current);
      frame.current = 0;
    };
  }, [playing, speed, duration]);

  // 탭이 가려지면 타이머를 멈춘다. 목업 visibilitychange 와 같은 규칙이다.
  useEffect(() => {
    const onHidden = () => { if (document.hidden) stop(); };
    document.addEventListener("visibilitychange", onHidden);
    return () => document.removeEventListener("visibilitychange", onHidden);
  }, [stop]);

  return {
    t, playing, speed, setT, setSpeed,
    toggle: () => setPlaying((p) => !p),
    reset: () => { stop(); setT(0); },
    stop,
  };
}
