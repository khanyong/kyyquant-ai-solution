import React from 'react'
import { useTranslation } from 'react-i18next'
import { Select, MenuItem, FormControl, InputLabel, SelectChangeEvent } from '@mui/material'

export default function LanguageSwitcher() {
  const { i18n, t } = useTranslation()

  const handleChange = (event: SelectChangeEvent) => {
    i18n.changeLanguage(event.target.value)
  }

  return (
    <FormControl size="small" sx={{ minWidth: 120 }}>
      <InputLabel id="language-select-label">{t('settings.language')}</InputLabel>
      <Select
        labelId="language-select-label"
        id="language-select"
        value={i18n.language}
        label={t('settings.language')}
        onChange={handleChange}
      >
        <MenuItem value="ko">한국어</MenuItem>
        <MenuItem value="en">English</MenuItem>
      </Select>
    </FormControl>
  )
}
