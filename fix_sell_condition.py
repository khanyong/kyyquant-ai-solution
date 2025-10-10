#!/usr/bin/env python3
"""
StrategyAnalyzer.tsx의 매도 조건 표시 부분을 수정하는 스크립트
"""

import re

# 파일 읽기
file_path = r'd:\Dev\auto_stock\src\components\StrategyAnalyzer.tsx'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 찾을 패턴 (522-533라인)
old_pattern = r'''      \) : \(
                        <Box>
                          <Typography variant="body2" sx=\{\{ mb: 2 \}\}>
                            매도 조건이 설정되지 않았습니다\.
                          </Typography>
                          <Alert severity="info">
                            <Typography variant="caption">
                              전략 빌더에서 매도 조건을 추가해주세요\.
                            </Typography>
                          </Alert>
                        </Box>
                      \)\}'''

# 새 코드
new_code = '''      ) : (
                        <Box>
                          {/* 지표 기반 매도 조건이 없어도, 목표수익률/손절이 있으면 표시 */}
                          {(selectedStrategy?.targetProfit || selectedStrategy?.stopLoss) ? (
                            <Box>
                              <Typography variant="body2" sx={{ mb: 2 }}>
                                지표 기반 매도 조건은 없지만, 다음 리스크 관리 설정으로 매도가 진행됩니다:
                              </Typography>

                              {/* 목표수익률 */}
                              {selectedStrategy?.targetProfit && (
                                <Box sx={{ mb: 2 }}>
                                  {selectedStrategy.targetProfit.mode === 'simple' && selectedStrategy.targetProfit.simple?.enabled && (
                                    <Box sx={{ mb: 1 }}>
                                      <Chip
                                        label="목표수익률"
                                        size="small"
                                        sx={{ mr: 1, bgcolor: 'success.dark' }}
                                      />
                                      <Typography variant="body2" component="span">
                                        수익률이 {selectedStrategy.targetProfit.simple.value}% 도달 시 매도
                                      </Typography>
                                    </Box>
                                  )}

                                  {selectedStrategy.targetProfit.mode === 'staged' && selectedStrategy.targetProfit.staged?.enabled && (
                                    <Box>
                                      <Chip
                                        label="단계별 목표수익률"
                                        size="small"
                                        sx={{ mr: 1, bgcolor: 'success.dark' }}
                                      />
                                      <Typography variant="body2" sx={{ mb: 1 }}>
                                        단계별 매도:
                                      </Typography>
                                      {selectedStrategy.targetProfit.staged.stages?.map((stage: any, idx: number) => (
                                        <Box key={idx} sx={{ ml: 2, mb: 0.5 }}>
                                          <Typography variant="caption" display="block">
                                            • {stage.stage}단계: {stage.targetProfit}% 도달 시 {stage.exitRatio}% 매도
                                            {stage.dynamicStopLoss && ' (동적 손절 활성화)'}
                                          </Typography>
                                        </Box>
                                      ))}
                                    </Box>
                                  )}
                                </Box>
                              )}

                              {/* 손절 */}
                              {selectedStrategy?.stopLoss?.enabled && (
                                <Box sx={{ mb: 1 }}>
                                  <Chip
                                    label="손절"
                                    size="small"
                                    sx={{ mr: 1, bgcolor: 'error.dark' }}
                                  />
                                  <Typography variant="body2" component="span">
                                    손실이 {Math.abs(selectedStrategy.stopLoss.value)}% 도달 시 매도
                                  </Typography>
                                  {selectedStrategy.stopLoss.breakEven?.enabled && (
                                    <Typography variant="caption" display="block" sx={{ ml: 6 }}>
                                      (본전 손절: {selectedStrategy.stopLoss.breakEven.threshold}% 이상 수익 시 활성화)
                                    </Typography>
                                  )}
                                  {selectedStrategy.stopLoss.trailingStop?.enabled && (
                                    <Typography variant="caption" display="block" sx={{ ml: 6 }}>
                                      (트레일링 손절: 최고점 대비 {selectedStrategy.stopLoss.trailingStop.distance}% 하락 시)
                                    </Typography>
                                  )}
                                </Box>
                              )}

                              <Alert severity="warning" sx={{ mt: 2 }}>
                                <Typography variant="caption">
                                  <strong>해석:</strong> 수익률 기반 자동 매도 전략 (지표 조건 없음)
                                </Typography>
                              </Alert>
                            </Box>
                          ) : (
                            <Box>
                              <Typography variant="body2" sx={{ mb: 2 }}>
                                매도 조건이 설정되지 않았습니다.
                              </Typography>
                              <Alert severity="info">
                                <Typography variant="caption">
                                  전략 빌더에서 매도 조건 또는 목표수익률/손절을 추가해주세요.
                                </Typography>
                              </Alert>
                            </Box>
                          )}
                        </Box>
                      )}'''

# 정규식으로 교체
result = re.sub(old_pattern, new_code, content, flags=re.MULTILINE)

if result == content:
    print("❌ 패턴을 찾지 못했습니다. 수동으로 수정이 필요합니다.")
    print("\n찾을 텍스트:")
    print("매도 조건이 설정되지 않았습니다.")
else:
    # 백업
    with open(file_path + '.backup', 'w', encoding='utf-8') as f:
        f.write(content)

    # 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(result)

    print("✅ 파일이 성공적으로 수정되었습니다!")
    print(f"백업 파일: {file_path}.backup")
