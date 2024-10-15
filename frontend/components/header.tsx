import { title, subtitle } from "@/components/primitives";

export default function Header() {
  return (
    <div className="inline-block max-w-xl text-center justify-center">
      <span className={title()}>Chat with your&nbsp;</span>
      <span className={title({ color: "yellow" })}>
        favorite NarutoVerse&nbsp;
      </span>
      <span className={title()}>characters!</span>
      <div className={subtitle({ class: "mt-4" })}>
        Beautiful, fast and modern React UI library.
      </div>
    </div>
  );
}
