import { AssetProfile } from '../utils/SimulationEngine';

export const SIMULATION_ASSETS: AssetProfile[] = [
    {
        id: 'us_sp500',
        name: '미국 S&P 500 ETF',
        category: 'equity',
        riskLevel: 3,
        expectedReturn: 10.5,
        dividendYield: 1.5,
        isTaxEfficient: false,
        allowedAccounts: ['general', 'pension', 'irp'],
        description: '글로벌 자산 배분의 핵심 코어 자산입니다. 미국 주식시장을 대표하는 500개 우량 기업에 분산 투자하여, 개별 기업 리스크를 배제하고 시장 전체의 성장을 향유할 수 있습니다. 장기 연금 투자의 기본이 되는 상품입니다.',
        pros: ['세계 최고의 혁신 기업들에 자동 분산 투자', '지난 100년간 검증된 우상향 자산', '달러 보유로 인한 경제 위기 방어 효과'],
        cons: ['단기적인 시장 변동성 (-20% 이상 하락 가능)', '환율 하락 시 원화 환산 수익률 감소'],
        maxDrawdown: -55.0,
        quantScore: 4.8,
        factorGrades: {
            valuation: 'C',
            growth: 'A',
            profitability: 'A+',
            momentum: 'A',
            revisions: 'B+'
        },
        dividendStats: {
            payoutRatio: 35,
            growthRate5Y: 6.5,
            growthStreak: 12,
            yieldTTM: 1.55
        },
        volatility: 16.5 // S&P 500 Historical StdDev
    },
    {
        id: 'kr_kospi',
        name: '한국 KOSPI 200',
        category: 'equity',
        riskLevel: 4,
        expectedReturn: 8.0,
        dividendYield: 2.5,
        isTaxEfficient: true,
        allowedAccounts: ['general', 'pension', 'irp'],
        description: '대한민국 경제를 이끄는 삼성전자, SK하이닉스, 현대차 등 대표 200개 기업에 투자합니다. 수출 중심의 한국 경제 특성상 글로벌 경기 사이클에 민감하게 반응합니다.',
        pros: ['일반 계좌에서 매매차익 완전 비과세 (세금 혜택)', '익숙한 국내 기업 투자', '배당 수익률 상승 추세'],
        cons: ['미국 대비 낮은 자본 효율성 (코리아 디스카운트)', '장기 우상향보다는 박스권 등락 경향', '원화 자산 집중 위험'],
        maxDrawdown: -50.0,
        quantScore: 3.2,
        factorGrades: {
            valuation: 'A-',
            growth: 'C',
            profitability: 'B',
            momentum: 'D+',
            revisions: 'C-'
        },
        dividendStats: {
            payoutRatio: 25,
            growthRate5Y: 4.2,
            growthStreak: 0,
            yieldTTM: 2.1
        },
        volatility: 18.2 // KOSPI is slightly more volatile
    },
    {
        id: 'us_tlt',
        name: '미국 장기채 (TLT)',
        category: 'bond',
        riskLevel: 2,
        expectedReturn: 4.5,
        dividendYield: 3.5,
        isTaxEfficient: false,
        allowedAccounts: ['general', 'pension', 'irp'],
        description: '미국 정부가 보증하는 20년 만기 이상의 초장기 국채입니다. 일반적으로 주식 시장 과열 시 하락하고, 경기 침체나 위기 시 상승하는 "주식 방어" 성격을 가집니다.',
        pros: ['경제 위기 시 주가 하락을 상쇄하는 헷지(Hedge) 효과', '안정적인 달러 이자 소득 (연 3~4% 수준)', '최고의 안전 자산 (미국 정부 보증)'],
        cons: ['금리 상승 시 채권 가격의 급격한 하락', '인플레이션 시 실질 수익률 저하'],
        maxDrawdown: -45.0,
        quantScore: 3.5,
        factorGrades: {
            valuation: 'B',
            growth: 'F',
            profitability: 'N/A',
            momentum: 'D',
            revisions: 'C'
        },
        dividendStats: {
            payoutRatio: 100,
            growthRate5Y: -2.0,
            growthStreak: 0,
            yieldTTM: 3.8
        },
        volatility: 14.0 // Long term bonds are volatile
    },
    {
        id: 'jepi',
        name: 'JEPI (고배당 커버드콜)',
        category: 'structured',
        riskLevel: 3,
        expectedReturn: 7.0,
        dividendYield: 8.0,
        isTaxEfficient: false,
        allowedAccounts: ['general', 'pension'],
        description: '주식 포트폴리오를 보유함과 동시에 "콜옵션 매도" 전략을 사용하여 추가적인 현금 흐름을 창출하는 상품입니다. 주가 상승 제한을 대가로 높은 월 배당을 받습니다.',
        pros: ['은퇴자에게 적합한 매월 높은 현금 흐름 (연 8~10%)', '주식 시장 횡보 또는 완만한 하락 시 방어력 우수'],
        cons: ['대세 상승장에서 시장 수익률을 따라가지 못함 (이익 제한)', '원금 손실 가능성이 있는 중위험 상품'],
        maxDrawdown: -20.0,
        quantScore: 4.2,
        factorGrades: {
            valuation: 'B+',
            growth: 'C+',
            profitability: 'A-',
            momentum: 'B',
            revisions: 'A'
        },
        dividendStats: {
            payoutRatio: 98,
            growthRate5Y: 8.5,
            growthStreak: 2,
            yieldTTM: 7.8
        },
        volatility: 12.5 // Lower volatility due to covered call
    },
    {
        id: 'schd',
        name: 'SCHD (미국 배당성장)',
        category: 'equity',
        riskLevel: 3,
        expectedReturn: 9.5,
        dividendYield: 3.5,
        isTaxEfficient: false,
        allowedAccounts: ['general', 'pension', 'irp'],
        description: '단순히 배당을 많이 주는 기업이 아니라, 10년 이상 배당금을 "꾸준히 늘려온" 현금 흐름이 우수한 기업(코카콜라, 펩시, 브로드컴 등)에 투자합니다.',
        pros: ['물가 상승을 헷지하는 배당 성장 (월급처럼 오르는 배당)', '재무 건전성이 입증된 우량주 위주', '장기 복리 투자의 정석'],
        cons: ['기술주(성장주) 중심의 강세장에서 상대적 소외 가능성'],
        maxDrawdown: -33.0,
        quantScore: 4.9,
        factorGrades: {
            valuation: 'A',
            growth: 'B+',
            profitability: 'A+',
            momentum: 'B-',
            revisions: 'A-'
        },
        dividendStats: {
            payoutRatio: 45,
            growthRate5Y: 11.8,
            growthStreak: 12,
            yieldTTM: 3.45
        },
        volatility: 15.0
    },
    {
        id: 'elw_call',
        name: 'ELW/옵션 (초고위험)',
        category: 'derivative',
        riskLevel: 5,
        expectedReturn: 25.0,
        dividendYield: 0,
        isTaxEfficient: false,
        allowedAccounts: ['general'],
        description: '주식/지수의 방향성에 레버리지를 걸어 베팅하는 파생상품입니다. 적은 금액으로 큰 수익을 낼 수 있지만, 예측이 빗나가면 만기 시 원금 100%가 소멸됩니다.',
        pros: ['적은 자본으로 10배~100배 이상의 수익 기회 (레버리지)', '단기 헷지 수단으로 활용 가능'],
        cons: ['시간이 지날수록 가치가 하락함 (시간 가치 소멸)', '원금 전액 손실 가능성 매우 높음', '노후 자금 운용에는 부적합'],
        maxDrawdown: -100.0,
        quantScore: 1.5,
        factorGrades: {
            valuation: 'D',
            growth: 'A+',
            profitability: 'F',
            momentum: 'A',
            revisions: 'D'
        },
        dividendStats: {
            payoutRatio: 0,
            growthRate5Y: 0,
            growthStreak: 0,
            yieldTTM: 0
        },
        volatility: 80.0 // Extremely high volatility
    }
];
