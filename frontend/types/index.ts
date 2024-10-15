import { SVGProps } from "react";

export type IconSvgProps = SVGProps<SVGSVGElement> & {
  size?: number;
};

export type Character = {
  id?: string;
  name?: string;
  href?: string;
  image_url?: string;
  summary?: string;
  information?: Record<string, any>;
};
