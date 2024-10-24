import { useEffect, useState } from "react";

interface WindowSize {
  width: number;
  height: number;
  deviceType: "mobile" | "tablet" | "desktop";
}

function useWindowSize() {
  const [windowSize, setWindowSize] = useState<WindowSize>({
    width: 1,
    height: 1,
    deviceType: "desktop", // Default device type
  });

  useEffect(() => {
    function handleResize() {
      const width = window.innerWidth;
      const height = window.innerHeight;

      // Determine device type based on the width
      const deviceType =
        width <= 768 ? "mobile" : width <= 1024 ? "tablet" : "desktop";

      setWindowSize({
        width,
        height,
        deviceType,
      });
    }

    window.addEventListener("resize", handleResize);
    handleResize();

    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return windowSize;
}

export default useWindowSize;
