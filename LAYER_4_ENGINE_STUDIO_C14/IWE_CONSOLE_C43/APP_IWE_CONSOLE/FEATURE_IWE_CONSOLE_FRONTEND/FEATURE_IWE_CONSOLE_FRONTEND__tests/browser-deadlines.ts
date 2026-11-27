export const browserDeadlinesEnabled = process.env.ANECHOIC_TEST_IMAGE_DEADLINES !== '0';

export function browserTimeout(milliseconds: number): number {
  return browserDeadlinesEnabled ? milliseconds : 0;
}
