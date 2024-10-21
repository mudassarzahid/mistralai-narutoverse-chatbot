export type SiteConfig = typeof siteConfig;

export const siteConfig = {
  name: "NarutoVerse Chatbot",
  description: "Chat with your favorite NarutoVerse Characters",
  navItems: [
    {
      label: "Home",
      href: "/",
    },
    {
      label: "Chat",
      href: "/chat",
    },
  ],
  navMenuItems: [],
  links: {
    github: "https://github.com/mudassarzahid/mistralai-narutoverse-chatbot",
  },
};
