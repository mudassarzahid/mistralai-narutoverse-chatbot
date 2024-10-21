const widthClasses = ["w-2/5", "w-3/5", "w-4/5"];

export function getRandomWidthClass(): string {
  return widthClasses[Math.floor(Math.random() * widthClasses.length)];
}
