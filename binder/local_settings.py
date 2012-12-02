### Local settings to be shared across modules.

TTL_CHOICES = ((300, "5 minutes"),
               (1800, "30 minutes"),
               (3600, "1 hour"),
               (43200, "12 hours"),
               (86400, "1 day"))

RECORD_TYPE_CHOICES = (("A", "A"),
                       ("AAAA", "AAAA"),
                       ("CNAME", "CNAME"))
