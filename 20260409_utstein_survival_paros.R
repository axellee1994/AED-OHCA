library(tidyverse)
library(DiagrammeR)
library(glue)

dat <- read_csv("D:/NUS Dropbox/Rop Fun Quek/backup_legion_20250805/hsrc/scdf_analytics/paros_new/Paros_SG_Apr10-Dec21_with postal codes_12Jan24.csv")

dat <- dat %>% mutate(`Date of Incident` = as.Date(`Date of Incident`, format = "%d/%m/%Y")) %>% mutate(year = year(`Date of Incident`))

dat_2 <- dat %>% filter(year %in% 2010:2017) 

dat_2 <- dat_2 %>% 
  mutate(witness = ifelse(`Arrest witnessed by` %in% c("Bystander - Family", 
                                                       "Bystander - Healthcare provider", 
                                                       "Bystander - Lay person", 
                                                       "Bystander - Lay Person"), 
                          "Bystander witnessed", `Arrest witnessed by`))

dat_2 %>% select(year, `Arrest witnessed by`) %>% table
dat_2 %>% select(year, witness) %>% table

dat_2 %>% filter(witness == "Bystander witnessed") %>% select(year, `First arrest rhythm`) %>% table
dat_2 <- dat_2 %>%
  mutate(first_arrest_rhythm = ifelse(`First arrest rhythm` %in% c("Unknown shockable rhythm", 
                                                                   "VF", "VT"), 
                                      "First rhythm shockable", 
                                      ifelse(`First arrest rhythm` %in% c("N/A", "Unknown", "Unknown Unshockable Rhythm"), "First rhythm unknown", "First rhythm unshockable")))
dat_2 %>% filter(witness == "Bystander witnessed") %>% select(year, first_arrest_rhythm) %>% table


dat_2 %>% filter(witness == "Bystander witnessed" & first_arrest_rhythm == "First rhythm shockable") %>% select(year, `Patient status`) %>% table
dat_2[dat_2$`Patient status` == ]

dat_2 <- dat_2 %>%
  mutate(patient_status = ifelse(patient_status %in% c("Discharged alive", "Discharged Alive"), "Discharged alive", 
                                 ifelse(patient_status %in% c("Died in the hospital"), "Died", 
                                        ifelse(`Outcome of patient` == "Died in ED", "Died", patient_status))))

dat_2 %>% filter(witness == "Bystander witnessed" & first_arrest_rhythm == "First rhythm shockable") %>% select(year, patient_status) %>% table

dat_2 %>% filter(is.na(patient_status)) %>% select()


cohort_summary <- dat_2 %>% 
  group_by(year) %>% tally() %>% 
  left_join(dat_2 %>% group_by(year, witness) %>% tally %>% spread(witness, n)) %>%
  left_join(dat_2 %>% filter(witness == "Bystander witnessed") %>% group_by(year, first_arrest_rhythm) %>% tally %>% spread(first_arrest_rhythm, n)) %>%
  left_join(dat_2 %>% filter(witness == "Bystander witnessed" & first_arrest_rhythm == "First rhythm shockable") %>% group_by(year, patient_status) %>% tally %>% spread(patient_status, n))


utstein_cases <- dat_2 %>% filter(witness == "Bystander witnessed" & first_arrest_rhythm == "First rhythm shockable") %>% select(`Case #`, year)
write_csv(utstein_cases, "20260409_utstein_paros.csv", na="")


cohort_summary2 <- cohort_summary %>%
  rename(
    total = n,
    bystander = `Bystander witnessed`,
    ems = `EMS/Private ambulance`,
    not_witnessed = `Not witnessed`,
    shockable = `First rhythm shockable`,
    unknown = `First rhythm unknown`,
    unshockable = `First rhythm unshockable`,
    died = Died,
    discharged_alive = `Discharged alive`,
    in_hospital_30d = `Remains in hospital at 30th day post arrest`
  )

plot_cohort_year2 <- function(cohort_summary, yr) {
  
  x <- cohort_summary %>% filter(year == yr)
  
  grViz(sprintf("
  digraph cohort {
    graph [layout = dot, rankdir = TB]
    
    node [shape = box, style = 'rounded,filled', fillcolor = '#F7F7F7']
    edge [color = '#9BB6E5']
    
    year [label = '%d', shape = plaintext, fontsize = 20]
    total [label = 'TOTAL\n%d', color = '#6F8FBF', penwidth = 2]
    
    notw [label = 'NOT\nWITNESSED\n%d']
    byw  [label = 'BYSTANDER\nWITNESSED\n%d']
    emsw [label = 'EMS\nWITNESSED\n%d']
    
    unsh [label = 'FIRST RHYTHM\nUNSHOCKABLE\n%d']
    shoc [label = 'FIRST RHYTHM\nSHOCKABLE\n%d']
    unk  [label = 'FIRST RHYTHM\nUNKNOWN\n%d']
    
    died  [label = 'DIED\n%d']
    alive [label = 'DISCHARGED\nALIVE\n%d', color = '#8BCF7A', penwidth = 2]
    hosp  [label = 'IN HOSPITAL\nAFTER 30 DAYS\n%d', color = '#8BCF7A', penwidth = 2]
    
    {rank = same; notw; byw; emsw}
    {rank = same; unsh; shoc; unk}
    {rank = same; died; alive; hosp}
    
    year -> total [style = invis]
    total -> notw
    total -> byw
    total -> emsw
    byw -> unsh
    byw -> shoc
    byw -> unk
    shoc -> died
    shoc -> alive
    shoc -> hosp
  }
  ",
                yr,
                x$total,
                x$not_witnessed,
                x$bystander,
                x$ems,
                x$unshockable,
                x$shockable,
                x$unknown,
                x$died,
                x$discharged_alive,
                x$in_hospital_30d
  ))
}

plot_cohort_year2(cohort_summary2, 2010)

plots <- lapply(2010:2017, function(yr) {
  plot_cohort_year2(cohort_summary2, yr)
})

names(plots) <- 2010:2017

html_file <- "cohort_grid.html"

library(htmlwidgets)
library(htmltools)
library(webshot2)

widget <- browsable(
  tagList(
    div(
      style = "display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;",
      plots
    )
  )
)

htmltools::save_html(widget, "temp.html")

webshot(
  "temp.html",
  "cohort_grid.png",
  vwidth = 4500,
  vheight = 2500,
  zoom = 2
)



plot_dat <- cohort_summary2 %>% select(year, shockable, died) %>% rename(OHCAs = shockable,  Expired = died) %>% mutate(Survived = OHCAs - Expired)
plot_dat <- plot_dat %>% mutate(survival_rate = Survived/OHCAs)

library(scales)

p <- ggplot(plot_dat, aes(x = year, y = survival_rate)) +
  geom_line(color = "black", linewidth = 0.8) +
  geom_point(size = 3) +
  
  # percentage labels above points
  geom_text(
    aes(label = paste0(round(survival_rate * 100), "%")),
    vjust = -1,
    size = 4
  ) +
  
  scale_y_continuous(
    labels = percent_format(accuracy = 1),
    limits = c(0, 0.25),
    breaks = seq(0, 0.25, 0.05)
  ) +
  
  scale_x_continuous(
    breaks = plot_dat$year
  ) +
  
  labs(
    title = "Utstein Survival Rate",
    x = NULL,
    y = NULL
  ) +
  
  theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold"),
    panel.grid.major.x = element_blank(),
    panel.grid.minor = element_blank()
  )

p

library(gridExtra)

table_dat <- plot_dat %>%
  select(year, OHCAs, Survived, Expired)

table_dat <- rbind(
  c("", plot_dat$year),
  c("OHCAs", plot_dat$OHCAs),
  c("Survived", plot_dat$Survived),
  c("Expired", plot_dat$Expired)
)

table_dat <- as.data.frame(table_dat)       

library(grid)

table_grob <- tableGrob(table_dat, rows = NULL)

png("utstein_survival.png")
grid.arrange(
  p,
  table_grob,
  ncol = 1,
  heights = c(3, 1)
)
dev.off()

