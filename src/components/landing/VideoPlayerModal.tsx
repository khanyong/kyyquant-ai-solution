import React, { useState, useRef, useEffect } from 'react'
import {
  Modal,
  Box,
  IconButton,
  Stack,
  Backdrop,
  Typography,
  alpha,
  Fade,
  Slider,
  Button
} from '@mui/material'
import {
  Close,
  PlayArrow,
  Pause,
  VolumeUp,
  VolumeOff,
  Fullscreen,
  FullscreenExit,
  ArrowForward
} from '@mui/icons-material'

interface VideoPlayerModalProps {
  open: boolean
  onClose: () => void
  videoSrc: string
  onCtaClick?: () => void
}

const VideoPlayerModal: React.FC<VideoPlayerModalProps> = ({
  open,
  onClose,
  videoSrc,
  onCtaClick
}) => {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [playing, setPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [muted, setMuted] = useState(false)
  const [fullscreen, setFullscreen] = useState(false)
  const [showControls, setShowControls] = useState(true)
  const [videoEnded, setVideoEnded] = useState(false)
  const controlsTimeoutRef = useRef<NodeJS.Timeout>()

  useEffect(() => {
    if (open && videoRef.current) {
      // Auto-play when modal opens
      videoRef.current.play()
      setPlaying(true)
    }
  }, [open])

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const handleTimeUpdate = () => setCurrentTime(video.currentTime)
    const handleLoadedMetadata = () => setDuration(video.duration)
    const handleEnded = () => {
      setPlaying(false)
      setVideoEnded(true)
    }

    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('loadedmetadata', handleLoadedMetadata)
    video.addEventListener('ended', handleEnded)

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate)
      video.removeEventListener('loadedmetadata', handleLoadedMetadata)
      video.removeEventListener('ended', handleEnded)
    }
  }, [])

  const handlePlayPause = () => {
    if (!videoRef.current) return

    if (playing) {
      videoRef.current.pause()
    } else {
      videoRef.current.play()
      setVideoEnded(false)
    }
    setPlaying(!playing)
  }

  const handleSeek = (_event: Event, newValue: number | number[]) => {
    if (!videoRef.current) return
    const time = newValue as number
    videoRef.current.currentTime = time
    setCurrentTime(time)
  }

  const handleVolumeChange = (_event: Event, newValue: number | number[]) => {
    if (!videoRef.current) return
    const vol = newValue as number
    videoRef.current.volume = vol
    setVolume(vol)
    setMuted(vol === 0)
  }

  const handleMuteToggle = () => {
    if (!videoRef.current) return
    const newMuted = !muted
    videoRef.current.muted = newMuted
    setMuted(newMuted)
  }

  const handleFullscreenToggle = () => {
    if (!videoRef.current) return

    if (!fullscreen) {
      if (videoRef.current.requestFullscreen) {
        videoRef.current.requestFullscreen()
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen()
      }
    }
    setFullscreen(!fullscreen)
  }

  const handleMouseMove = () => {
    setShowControls(true)
    if (controlsTimeoutRef.current) {
      clearTimeout(controlsTimeoutRef.current)
    }
    controlsTimeoutRef.current = setTimeout(() => {
      if (playing) {
        setShowControls(false)
      }
    }, 3000)
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const handleClose = () => {
    if (videoRef.current) {
      videoRef.current.pause()
      videoRef.current.currentTime = 0
    }
    setPlaying(false)
    setVideoEnded(false)
    onClose()
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      closeAfterTransition
      slots={{ backdrop: Backdrop }}
      slotProps={{
        backdrop: {
          timeout: 500,
          sx: {
            backdropFilter: 'blur(20px)',
            backgroundColor: alpha('#000000', 0.9)
          }
        }
      }}
    >
      <Fade in={open}>
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: { xs: '95%', sm: '90%', md: '85%', lg: '80%' },
            maxWidth: '1400px',
            outline: 'none'
          }}
          onMouseMove={handleMouseMove}
          onMouseLeave={() => playing && setShowControls(false)}
        >
          {/* Close Button */}
          <Fade in={showControls || !playing}>
            <IconButton
              onClick={handleClose}
              sx={{
                position: 'absolute',
                top: -60,
                right: 0,
                color: '#FFFFFF',
                backgroundColor: alpha('#000000', 0.5),
                backdropFilter: 'blur(10px)',
                '&:hover': {
                  backgroundColor: alpha('#000000', 0.7),
                  transform: 'scale(1.1)'
                },
                transition: 'all 0.3s ease',
                zIndex: 10
              }}
            >
              <Close />
            </IconButton>
          </Fade>

          {/* Video Container */}
          <Box
            sx={{
              position: 'relative',
              width: '100%',
              aspectRatio: '16/9',
              borderRadius: 3,
              overflow: 'hidden',
              backgroundColor: '#000000',
              boxShadow: `0 24px 80px ${alpha('#000000', 0.8)}`
            }}
          >
            <video
              ref={videoRef}
              src={videoSrc}
              style={{
                width: '100%',
                height: '100%',
                display: 'block'
              }}
              onClick={handlePlayPause}
            />

            {/* Play/Pause Overlay Button */}
            {!playing && !videoEnded && (
              <Fade in={true}>
                <Box
                  sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    zIndex: 2
                  }}
                >
                  <IconButton
                    onClick={handlePlayPause}
                    sx={{
                      width: 80,
                      height: 80,
                      backgroundColor: alpha('#FFB800', 0.9),
                      color: '#000000',
                      '&:hover': {
                        backgroundColor: '#FFB800',
                        transform: 'scale(1.1)'
                      },
                      transition: 'all 0.3s ease'
                    }}
                  >
                    <PlayArrow sx={{ fontSize: 50 }} />
                  </IconButton>
                </Box>
              </Fade>
            )}

            {/* Video Ended CTA */}
            {videoEnded && (
              <Fade in={true}>
                <Box
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: alpha('#000000', 0.7),
                    backdropFilter: 'blur(10px)',
                    zIndex: 3
                  }}
                >
                  <Stack spacing={3} alignItems="center">
                    <Typography
                      variant="h4"
                      sx={{
                        color: '#FFFFFF',
                        fontWeight: 700,
                        textAlign: 'center'
                      }}
                    >
                      지금 바로 시작하세요
                    </Typography>
                    <Stack direction="row" spacing={2}>
                      <Button
                        variant="contained"
                        size="large"
                        endIcon={<ArrowForward />}
                        onClick={() => {
                          handleClose()
                          onCtaClick?.()
                        }}
                        sx={{
                          py: 1.5,
                          px: 4,
                          fontWeight: 700,
                          background: 'linear-gradient(135deg, #FFB800 0%, #FF8A00 100%)',
                          boxShadow: `0 8px 32px ${alpha('#FFB800', 0.4)}`,
                          '&:hover': {
                            boxShadow: `0 12px 48px ${alpha('#FFB800', 0.6)}`,
                            transform: 'translateY(-2px)'
                          }
                        }}
                      >
                        무료로 시작하기
                      </Button>
                      <Button
                        variant="outlined"
                        size="large"
                        onClick={handlePlayPause}
                        sx={{
                          py: 1.5,
                          px: 4,
                          fontWeight: 700,
                          borderColor: '#FFFFFF',
                          color: '#FFFFFF',
                          '&:hover': {
                            borderColor: '#FFB800',
                            color: '#FFB800',
                            backgroundColor: alpha('#FFB800', 0.1)
                          }
                        }}
                      >
                        다시 보기
                      </Button>
                    </Stack>
                  </Stack>
                </Box>
              </Fade>
            )}

            {/* Controls */}
            <Fade in={showControls || !playing}>
              <Box
                sx={{
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  background: `linear-gradient(to top, ${alpha('#000000', 0.9)} 0%, transparent 100%)`,
                  backdropFilter: 'blur(10px)',
                  p: 2,
                  zIndex: 5
                }}
              >
                {/* Progress Bar */}
                <Slider
                  value={currentTime}
                  max={duration || 100}
                  onChange={handleSeek}
                  sx={{
                    mb: 1,
                    color: '#FFB800',
                    '& .MuiSlider-thumb': {
                      width: 16,
                      height: 16,
                      '&:hover': {
                        boxShadow: `0 0 0 8px ${alpha('#FFB800', 0.16)}`
                      }
                    },
                    '& .MuiSlider-track': {
                      height: 4
                    },
                    '& .MuiSlider-rail': {
                      height: 4,
                      opacity: 0.3
                    }
                  }}
                />

                <Stack direction="row" alignItems="center" spacing={2}>
                  {/* Play/Pause */}
                  <IconButton
                    onClick={handlePlayPause}
                    sx={{ color: '#FFFFFF', p: 1 }}
                  >
                    {playing ? <Pause /> : <PlayArrow />}
                  </IconButton>

                  {/* Time */}
                  <Typography variant="body2" sx={{ color: '#FFFFFF', minWidth: 100 }}>
                    {formatTime(currentTime)} / {formatTime(duration)}
                  </Typography>

                  <Box sx={{ flexGrow: 1 }} />

                  {/* Volume */}
                  <Stack direction="row" alignItems="center" spacing={1} sx={{ width: 150 }}>
                    <IconButton
                      onClick={handleMuteToggle}
                      sx={{ color: '#FFFFFF', p: 1 }}
                    >
                      {muted ? <VolumeOff /> : <VolumeUp />}
                    </IconButton>
                    <Slider
                      value={muted ? 0 : volume}
                      max={1}
                      step={0.1}
                      onChange={handleVolumeChange}
                      sx={{
                        color: '#FFFFFF',
                        '& .MuiSlider-thumb': {
                          width: 12,
                          height: 12
                        }
                      }}
                    />
                  </Stack>

                  {/* Fullscreen */}
                  <IconButton
                    onClick={handleFullscreenToggle}
                    sx={{ color: '#FFFFFF', p: 1 }}
                  >
                    {fullscreen ? <FullscreenExit /> : <Fullscreen />}
                  </IconButton>
                </Stack>
              </Box>
            </Fade>
          </Box>
        </Box>
      </Fade>
    </Modal>
  )
}

export default VideoPlayerModal
