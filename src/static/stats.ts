function slope(ys: number[], xs: number[]) {
  const n = ys.length
  let sumX = 0
  let sumY = 0
  let sumXY = 0
  let sumXX = 0
  let sumYY = 0

  for (let i = 0; i < n; i++) {
    const x = xs[i]
    const y = ys[i]
    sumX += x
    sumY += y
    sumXY += x * y
    sumXX += x * x
    sumYY += y * y
  }

  return (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX)
}
