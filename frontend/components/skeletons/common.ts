const defaultWidthClasses = ["w-2/5", "w-3/5", "w-4/5"];

export function getRandomWidthClass(
  widthClasses: string[] = defaultWidthClasses,
): string {
  return widthClasses[Math.floor(Math.random() * widthClasses.length)];
}
