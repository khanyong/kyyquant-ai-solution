"""
Supabase 우선 지표 계산 로직 수정 예시
"""

def calculate(self, df: pd.DataFrame, config: Dict[str, Any], options: Optional[ExecOptions] = None) -> IndicatorResult:
    """지표 계산 - Supabase 우선"""
    start_time = time.time()
    warnings = []

    # 기본 옵션
    if options is None:
        options = ExecOptions(
            period=config.get('params', {}).get('period', 20),
            realtime=config.get('realtime', False)
        )

    # 입력 검증
    df = self._validate_input(df, warnings)

    indicator_name = config.get('name')

    try:
        # 캐시 확인
        cache_key = self._get_cache_key(indicator_name, options)
        if cache_key in self._execution_cache:
            cached_result = self._execution_cache[cache_key]
            logger.info(f"Using cached result for {indicator_name}")
            return cached_result

        # ========================================
        # 1. Supabase 지표 먼저 확인 (우선순위 높음)
        # ========================================
        indicator_def = self.indicators_cache.get(indicator_name)
        if indicator_def:
            logger.info(f"Using Supabase definition for {indicator_name}")
            calc_type = indicator_def.get('calculation_type')

            if calc_type == 'built-in':
                # Supabase의 built-in 정의 사용
                method = json.loads(indicator_def.get('formula', '{}')).get('method')
                if method and method in self.registry._indicators:
                    result_columns = self.registry.execute(method, df, options)
                else:
                    # Supabase 정의대로 계산
                    result_columns = self._calculate_from_supabase_builtin(df, indicator_def, options)

            elif calc_type == 'custom_formula':
                # Supabase의 커스텀 수식
                result_columns = self._calculate_custom_formula(df, indicator_def, options)

            elif calc_type == 'python_code':
                # Supabase의 Python 코드
                result_columns = self._calculate_python_code(df, indicator_def, options)
            else:
                raise ValueError(f"Unknown calculation type in Supabase: {calc_type}")

        # ========================================
        # 2. 내장 지표 (Fallback)
        # ========================================
        elif indicator_name in self.registry._indicators:
            logger.info(f"Using built-in indicator for {indicator_name}")
            result_columns = self._calculate_builtin(df, indicator_name, options)

        # ========================================
        # 3. config에 calculation_type이 명시된 경우
        # ========================================
        elif 'calculation_type' in config:
            calc_type = config['calculation_type']
            if calc_type == 'custom_formula':
                result_columns = self._calculate_custom_formula(df, config, options)
            elif calc_type == 'python_code':
                result_columns = self._calculate_python_code(df, config, options)
            else:
                raise ValueError(f"Unknown calculation type: {calc_type}")
        else:
            raise ValueError(f"Unknown indicator: {indicator_name}")

        # 결과 생성
        execution_time = (time.time() - start_time) * 1000
        nan_ratio = self._calculate_nan_ratio(result_columns)

        result = IndicatorResult(
            columns=result_columns,
            metadata={
                'indicator': indicator_name,
                'source': 'supabase' if indicator_def else 'builtin',
                'engine': 'v3',
                'options': options.__dict__
            },
            execution_time_ms=execution_time,
            nan_ratio=nan_ratio,
            warnings=warnings
        )

        # 캐시 저장
        self._execution_cache[cache_key] = result

        # 로깅
        logger.info(f"Calculated {indicator_name} from {result.metadata['source']}: "
                   f"{len(result_columns)} columns, {execution_time:.2f}ms")

        return result

    except Exception as e:
        logger.error(f"Failed to calculate {indicator_name}: {e}")
        traceback.print_exc()
        raise

def _calculate_from_supabase_builtin(self, df: pd.DataFrame, definition: Dict, options: ExecOptions) -> Dict[str, pd.Series]:
    """Supabase built-in 지표 계산"""
    formula = definition.get('formula', {})
    if isinstance(formula, str):
        formula = json.loads(formula)

    method = formula.get('method', '').lower()
    source = formula.get('source', 'close')

    # 파라미터 병합
    default_params = definition.get('default_params', {})
    if isinstance(default_params, str):
        default_params = json.loads(default_params)

    params = {**default_params, **options.__dict__}
    period = params.get('period', 20)

    # 메서드별 계산
    if method in ['sma', 'ma', 'simple_moving_average']:
        return {'result': df[source].rolling(window=period).mean()}

    elif method in ['ema', 'exponential_moving_average']:
        return {'result': df[source].ewm(span=period, adjust=False).mean()}

    elif method == 'rsi':
        # RSI 계산 로직
        delta = df[source].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return {'result': rsi.clip(0, 100)}

    # 더 많은 메서드 추가 가능...
    else:
        raise ValueError(f"Unknown method: {method}")