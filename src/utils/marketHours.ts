/**
 * 주식시장 영업시간 체크 유틸리티
 */

/**
 * 현재 시간이 주식시장 영업시간인지 확인
 * 월~금 09:00 ~ 15:30 (KST)
 */
export function isMarketOpen(): boolean {
  const now = new Date()

  // KST (UTC+9) 시간으로 변환
  const kstOffset = 9 * 60 // 9시간을 분으로
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000)
  const kst = new Date(utc + (kstOffset * 60000))

  // 요일 체크 (0: 일요일, 6: 토요일)
  const dayOfWeek = kst.getDay()
  if (dayOfWeek === 0 || dayOfWeek === 6) {
    return false // 주말
  }

  // 시간 체크 (09:00 ~ 15:30)
  const hour = kst.getHours()
  const minute = kst.getMinutes()

  if (hour < 9) {
    return false // 9시 이전
  }

  if (hour > 15) {
    return false // 15시 이후
  }

  if (hour === 15 && minute > 30) {
    return false // 15시 30분 이후
  }

  return true
}

/**
 * 다음 시장 오픈 시간까지 남은 시간 (밀리초)
 */
export function getTimeUntilMarketOpen(): number {
  const now = new Date()

  // KST (UTC+9) 시간으로 변환
  const kstOffset = 9 * 60
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000)
  const kst = new Date(utc + (kstOffset * 60000))

  const dayOfWeek = kst.getDay()
  const hour = kst.getHours()

  // 다음 시장 오픈 시간 계산
  let daysUntilOpen = 0

  if (dayOfWeek === 0) {
    // 일요일 → 월요일
    daysUntilOpen = 1
  } else if (dayOfWeek === 6) {
    // 토요일 → 월요일
    daysUntilOpen = 2
  } else if (hour >= 15) {
    // 평일 15시 이후 → 다음 날 (금요일이면 월요일)
    daysUntilOpen = dayOfWeek === 5 ? 3 : 1
  }

  // 다음 오픈 시간 (09:00 KST)
  const nextOpen = new Date(kst)
  nextOpen.setDate(nextOpen.getDate() + daysUntilOpen)
  nextOpen.setHours(9, 0, 0, 0)

  return nextOpen.getTime() - kst.getTime()
}

/**
 * 시장 상태 메시지
 */
export function getMarketStatusMessage(): string {
  if (isMarketOpen()) {
    return '시장 운영 중'
  }

  const now = new Date()
  const kstOffset = 9 * 60
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000)
  const kst = new Date(utc + (kstOffset * 60000))

  const dayOfWeek = kst.getDay()
  const hour = kst.getHours()

  if (dayOfWeek === 0 || dayOfWeek === 6) {
    return '주말 - 시장 휴장'
  }

  if (hour < 9) {
    return '장 시작 전'
  }

  if (hour >= 15) {
    return '장 마감'
  }

  return '시장 휴장'
}
