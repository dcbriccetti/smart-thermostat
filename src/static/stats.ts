function slope(ys, xs) {
  const n = ys.length
  let sumX = 0
  let sumY = 0
  let sumXY = 0
  let sumXX = 0
  let sumYY = 0

  for (var i = 0; i < ys.length; i++) {
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
