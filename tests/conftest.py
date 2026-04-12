_cc_cstring = "user\x00"                         # NUL (Cc)
_cf_left_to_right = "Hey my name is \u200E"      # LEFT‑TO‑RIGHT MARK (Cf)
_cf_right_to_left = "Hey I am the ad\u200Fmin"   # RIGHT‑TO‑LEFT MARK (Cf)
_cf_zero_width = "your friend\u200B"             # ZERO‑WIDTH SPACE (Cf)

_co_private = "verifi\xE0\x80\x80ed"             # U+E000 (Co) in UTF‑8 bytes
_cs_low = "mode\xED\xA0\x80rator"                # U+D800 (Cs) surrogate in UTF‑8
_co_str = chr(0xE000) + "admin"                  # Private‑use char (Co)
_cs_str = "admin" + chr(0xD800)                  # Low‑surrogate (Cs)

ESOTERIC_STRINGS = [_cc_cstring, _cf_left_to_right, _cf_right_to_left,
                    _cf_zero_width, _co_private, _cs_low, _co_str, _cs_str]
WRONG_CONTENT_TYPES = ["text/html", "text/plain", "text/css", "text/javascript", 
                          "application/xml", "application/pdf", "image/png", "image/jpeg",
                          "audio/mpeg", "video/mp4", "multipart/form-data"]
