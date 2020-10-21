## Kodi PVR Chase Play Addon
This addon enables Kodi to seek while playing an in-progress recording and reaching the end of the video.

For example, if you record a program that is an hour long, and begin watching the recording after 15 minutes, Kodi will 
report the video's length as 15 minutes.  When you hit the 15 minute mark of the recording, Kodi will continue to play it
but any attempt to seek will bring the video back to the 15 minute mark. I 
believe this is a limiation with FFMpeg rather than Kodi.

This addon will catch an attempt to seek past the original duration of the video.
If the file has grown in size since playback began, the addon will re-start the video file (in order to load the updated
duration into Kodi) and set the current playing time to the desired seek location.  In the example above, if a seek
to the 16 minute mark was attempted, the addon will close the video, re-start it and set the current playing time
to 16 minutes (as long as the recording has reached at least 16 minutes in duration by this time).

### Limitations
1. Re-starting a video from an addon is not exactly seamless in Kodi.  The
user will see the video exit, a frame or two from the beginning as it restarts,
then it should jump to the correct location.
2. Progressive skip does not work well with this addon.  I recommend using fixed skip intervals.  With progressive
skip, the Kodi GUI will not let you skip past the video's duration, you can only skip to the end.  The addon should still
catch this and reload the video, but it's not as intuitive as fixed skip.  Additionally, if Kodi is playing beyond the
duration of the video (say we're watching at 16 minutes, but Kodi believes the end is at 15 minutes) attempting a progressive
skip will bring you back to the end of the video (e.g. the progressive skip can only be -1 minute).  The addon attempts
to catch this and bring you back to where the skip was attempted - the video will be reloaded and the current playing time
set to 16 minutes.
3. If a seek is attempted that exceeds the current recording time (e.g the video is reloaded and the requested seek still
exceeds the recorded video duration) the playing time will be set close to the end of the recorded video.  The default is
10s from the end, but this can be adjusted through the addon settings.  Note that Kodi behaves erratically with times that
are very close to the end of the current recording (10s is a pretty safe buffer).
