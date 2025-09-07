export class IndicatorConditionService {
  evaluateCondition(
    currentValue: number,
    operator: string,
    targetValue: number,
    previousValue?: number
  ): boolean {
    switch (operator) {
      case '>':
        return currentValue > targetValue;
      case '<':
        return currentValue < targetValue;
      case '>=':
        return currentValue >= targetValue;
      case '<=':
        return currentValue <= targetValue;
      case '==':
      case '=':
        return Math.abs(currentValue - targetValue) < 0.0001;
      case 'crosses_above':
        if (previousValue === undefined) return false;
        return previousValue <= targetValue && currentValue > targetValue;
      case 'crosses_below':
        if (previousValue === undefined) return false;
        return previousValue >= targetValue && currentValue < targetValue;
      default:
        return false;
    }
  }

  formatConditionText(indicator: string, operator: string, value: number): string {
    const operatorText: { [key: string]: string } = {
      '>': '보다 큼',
      '<': '보다 작음',
      '>=': '이상',
      '<=': '이하',
      '==': '같음',
      '=': '같음',
      'crosses_above': '상향 돌파',
      'crosses_below': '하향 돌파'
    };

    return `${indicator} ${operatorText[operator] || operator} ${value}`;
  }

  validateCondition(condition: any): boolean {
    if (!condition) return false;
    if (!condition.indicator || !condition.operator) return false;
    if (condition.value === undefined || condition.value === null) return false;
    return true;
  }

  parseConditionString(conditionStr: string): {
    indicator: string;
    operator: string;
    value: number;
  } | null {
    // Parse condition string like "RSI > 70"
    const match = conditionStr.match(/^(\w+)\s*([><=]+|crosses_above|crosses_below)\s*(\d+\.?\d*)$/);
    if (!match) return null;

    return {
      indicator: match[1],
      operator: match[2],
      value: parseFloat(match[3])
    };
  }
}

export const indicatorConditionService = new IndicatorConditionService();