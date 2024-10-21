import { SVGProps } from "react";

export type IconSvgProps = SVGProps<SVGSVGElement> & {
  size?: number;
};

export type Character = {
  id?: Number;
  name?: string;
  href?: string;
  image_url?: string;
  summary?: string;
};

export type Message = {
  sender: string;
  text: string;
};
