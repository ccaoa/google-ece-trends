## Functions for the google trends analysis

library(dplyr)
library(moments)


get_descriptive_stats_time <- function(data) {
  ## Remove the pull_date from this part of the analysis
  data <- subset(data, select = -c(pull_date))
  
  ## Mean for each day in the dataset
  average <- sapply(data, function(x) mean(x, na.rm = TRUE))
  
  ## Median for each day in the dataset
  median <- sapply(data, function(x) median(x, na.rm = TRUE))
  
  ## Min and Max for each day in the dataset
  min <- sapply(data, function(x) min(x, na.rm = TRUE))
  max <- sapply(data, function(x) max(x, na.rm = TRUE))
  
  ## Standard Deviation for each day in the dataset
  sd <- sapply(data, function(x) sd(x, na.rm = TRUE))
  
  ## Variance for each day in the dataset
  var <- sapply(data, function(x) var(x, na.rm = TRUE))
  
  ## Skewness for each day in the dataset
  skew <- sapply(data, function(x) skewness(x, na.rm = TRUE))
  
  ## Kurtosis for each day in the dataset
  kurtosis <- sapply(data, function(x) kurtosis(x, na.rm = TRUE))
  
  std_error <- sd /sqrt(length(data))
  ci_lower <- average - qnorm(0.975) * std_error
  ci_upper <- average + qnorm(0.975) * std_error
  
  ## compile each of these into a dataframe
  df <- as.data.frame(average)
  
  ## And in the darkness bind them!
  df <- cbind(df, median, min, max, sd, var, skew, kurtosis, ci_lower, ci_upper)
  
  
  return(df)
}

add_date_column <- function(data) {
  ## Takes a dataframe and adds a time column and converts it to a date
  ## This is set up specifically for the way the previous function stores the rownames
  
  ## Create the column
  data$time <- rownames(data)
  
  ## Convert that column into a date data type
  data$time <- as.Date(data$time)
  
  return(data)

}


add_geog_column <- function(data) {
  ## Takes a dataframe and adds a geog column and converts it to a factor
  ## This is set up specifically for the way the previous function stores the rownames
  
  ## Create column
  data$geog <- rownames(data)
  
  ## Convert it to a factor
  data$geog <- as.factor(data$geog)
  
  return(data)
}

## Function to get the popularity score from processed Google Trends Data.
## This function requires you run the get_descriptive_stats_time function before
get_popularity <- function(data) {
  pop_score <- mean(data$sd, na.rm = TRUE)
  
  return(pop_score)
}

## This function also requires you run the get_descriptive_stats_time function first
## This function will return a vector of MAPE scores for each period in the time series of data
get_mape <- function(truth_data, extracted_data) {
  mape <- mean(abs((truth_data$average - extracted_data$average)/truth_data$average), na.rm = TRUE) * 100
  
  return(mape)
}

## Get theoretical mape based on the relationship to number of extractions
## This is pulled the Cebrian 2024 paper equation 8
get_theoretical_mape <- function(popularity, extractions) {
  theoretical_mape <- 1.3728 * (popularity/sqrt(extractions)) + 0.0034 * (popularity**3/sqrt(extractions))
  
  return(theoretical_mape)
}




## This function pulls random samples from the population to create a smaller number
## of extracted samples
get_samples <- function(data,  num_samples) {
  s <- data %>% slice_sample(n = num_samples) %>% get_descriptive_stats_time() %>% add_date_column()
  
  ## add a source column so it can be nicely graphed with the other data
  s$source <- paste(num_samples, "Samples")
  
  return(s)
}


## This function will calculate the expected number of extraction needed based
## on the popularity score for each geographic area
get_expected_extractions <- function(data) {
  pop_score <- get_popularity(data)
  #mape <- get_theoretical_mape(pop_score, extractions)
  
  expected_extractions <- ((1.3728 * pop_score) + (0.0034 * pop_score**3))**2 / 5**2
  
  return(expected_extractions)
}


## I don't want to mess up the data input as I move through the different geographic regions
## So I'm going to create a couple functions for plotting and data cleaning

## Create a plot for comparing averages from different extractions
create_sample_average_plot <- function(data, truth_data) {
  one <- get_samples(data, 1)
  #print(get_expected_extractions(one))
  two <- get_samples(data, 2)
  #print(get_expected_extractions(two))
  five <- get_samples(data,5)
  #print(get_expected_extractions(five))
  ten <- get_samples(data,10)
  #print(get_expected_extractions(ten))
  twenty <- get_samples(data,20)
  #print(get_expected_extractions(twenty))
  fifty <- get_samples(data,50)
  #print(get_expected_extractions(fifty))
  hundred <- get_samples(data,100)
  #print(get_expected_extractions(hundred))
  two_hundred <- get_samples(data, 200)
  
  ## Create a dataframe of these extracted values
  df_samples <- rbind(one, two, five, ten, twenty, fifty, hundred, two_hundred)
  
  df_samples$source <- factor(df_samples$source, levels = c("1 Samples", "2 Samples", "5 Samples", "10 Samples", "20 Samples", "50 Samples", "100 Samples", "200 Samples"))
  
  ## Now plot all of these alongside the national level data
  the_plot <- ggplot(data = df_samples, aes(x = time, y = average, group = source)) + 
    geom_line(aes(color = source)) +
    #ggtitle("Average RSV - United States") + 
    theme(plot.title = element_text(hjust = 0.5)) +
    ylab("Relative Search Volume") +
    xlab("Date") +
    labs(fill = "Number of Samples", color = "Number of Samples") +
    theme(legend.position = "bottom")
    # geom_line(data = one, aes(x = time, y = average, group = source, color = source)) +
    # geom_line(data = two, aes(x = time, y = average, group = source, color = source)) +
    # geom_line(data = five, aes(x = time, y = average, group = source, color = source)) +
    # geom_line(data = ten, aes(x = time, y = average, group = source, color = source)) +
    # geom_line(data = twenty, aes(x = time, y = average, group = source, color = source)) +
    # geom_line(data = fifty, aes(x = time, y = average, group = source, color = source)) +
    # geom_line(data = hundred, aes(x = time, y = average, group = source, color = source))
  
  return(the_plot)
}


## Function runs the bootstrap for the number the average RSV across the different samples
boot_rsv <- function(data) {
  averages <- c()
  ci_uppers <- c()
  ci_lowers <- c()
  names <- c()
  
  for (i in c(1,2,5,10,20,50,100,200)) {
    ## The function for the bootstrap sampler
    boot_sampler <- function(input, idx, sample_size = i) {
      custom_indices <- sample(idx, sample_size, replace = T)
      sample_data <- input[custom_indices,] %>%
        get_descriptive_stats_time() %>%
        add_date_column()
      
      return(mean(sample_data$average))
    }
    
    ## Run the bootstrap function with the sampler above
    boot_rsv_result <- boot(data, boot_sampler, R = 2000)
    
    ## Examine the confidence intervals for the samples
    ci_boot <- boot.ci(boot_rsv_result, type = "perc")
    ci_lower <- ci_boot$percent[length(ci_boot$percent) - 1]
    ci_upper <- ci_boot$percent[length(ci_boot$percent)]
    ci_average <- mean(boot_rsv_result$t, na.rm = TRUE)
    name <- paste(i, "Samples")
    
    ## Append the values to the lists above
    averages <- c(averages, ci_average)
    ci_uppers <- c(ci_uppers, ci_upper)
    ci_lowers <- c(ci_lowers, ci_lower)
    names <- c(names, name)
  }
  
  ## Build a dataframe for plotting
  average_samples_df <- data.frame(averages, ci_uppers, ci_lowers, names)
  
}

## Create bootstrap function for expected number of extractions
expected_extractions <- function(data) {
  names <- c()
  mean_extractions <- c()
  ci_uppers <- c()
  ci_lowers <- c()
  
  for (i in c(2,5,10,20,50,100,200)) {
    
    ## The function for the bootstrap sampler
    boot_sampler <- function(input, idx, sample_size = i) {
      custom_indices <- sample(idx, sample_size, replace = T)
      sample_data <- input[custom_indices,] %>%
        get_descriptive_stats_time() %>%
        add_date_column()
      
      return(get_expected_extractions(sample_data))
    }
    
    ## Run the bootstrap for the expected number of extractions
    boot_extractions_results <- boot(data, boot_sampler, R = 2000)
    
    ## Examine the confidence intervals for the samples
    ci_boot <- boot.ci(boot_extractions_results, type = "perc")
    ci_lower <- ci_boot$percent[length(ci_boot$percent) - 1]
    ci_upper <- ci_boot$percent[length(ci_boot$percent)]
    ci_average <- mean(boot_extractions_results$t, na.rm = TRUE)
    name <- paste(i, "Samples")
    
    ## Append the the appropriate vectors
    mean_extractions <- c(mean_extractions, ci_average)
    ci_uppers <- c(ci_uppers, ci_upper)
    ci_lowers <- c(ci_lowers, ci_lower)
    names <- c(names, name)
  }
  
  ## Build dataframe for plotting
  expected_extractions_df <- data.frame(mean_extractions, ci_uppers, ci_lowers, names)
  
  expected_extractions_df$names <- factor(expected_extractions_df$names, levels = c("2 Samples", "5 Samples", "10 Samples", "20 Samples", "50 Samples", "100 Samples", "200 Samples"))
  
  return(expected_extractions_df)
}

## Create a comparison dataframe so I can compare the empirical and theoretical data
## Based on the methods from Cebrian 2024
create_comparison_df <- function(data, truth_data) {
  ## Holder vectors to create a dataframe afterward
  pop_scores <- c()
  mapes <- c()
  t_mapes <- c() ## theoretical mapes
  names <- c()
  ci_lowers <- c()
  ci_uppers <- c()
  expected_extractions <- c()
  
  for (i in c(1,2,5,10,20,50,100,200)) {
    ## Get the samples
    s <- get_samples(data, i)
    # print(paste(i,"The expected number of extractions for this sample is:",get_expected_extractions(s)))
    
    expected_extraction <- get_expected_extractions(s)
    
    ## get the popularity score
    pop_score <- get_popularity(s)
    
    ## get the mape
    mape <- get_mape(truth_data, s)
    
    ## get the theoretical map based on Cebrian 2024
    t_mape <- get_theoretical_mape(pop_score,i)
    
    ## get the label so it can be added to the new dataframe
    name <- unique(s$source)
    
    # get the bootstrapped CI values
    boot_func <- function(input, idx, sample_size = i) {
      custom_indices <- sample(idx, sample_size, replace = T)
      sample_data <- input[custom_indices,] %>%
        get_descriptive_stats_time() %>%
        add_date_column()

      return(get_mape(truth_data, sample_data))
    }

    boot_result <- boot(data, boot_func, R = 2000)
    ci_boot <- boot.ci(boot_result, type = "perc")
    ci_lower <- ci_boot$percent[length(ci_boot$percent) - 1]
    ci_upper <- ci_boot$percent[length(ci_boot$percent)]
    
    
    ## append them to the appropriate lists
    pop_scores <- c(pop_scores, pop_score)
    mapes <- c(mapes, mape)
    t_mapes <- c(t_mapes, t_mape)
    names <- c(names, name)
    expected_extractions <- c(expected_extractions, expected_extraction)
    ci_lowers <- c(ci_lowers, ci_lower)
    ci_uppers <- c(ci_uppers, ci_upper)
  }
  
  ## Build a dataframe from the data for plotting
  comparison_df <- data.frame(pop_scores, mapes, t_mapes, names, expected_extractions, ci_lowers, ci_uppers)
  
  ## Order the names so it prints coherently in the x-axis when plotted
  comparison_df$names <- factor(comparison_df$names, levels = c("1 Samples", "2 Samples", "5 Samples", "10 Samples", "20 Samples", "50 Samples", "100 Samples", "200 Samples"))
  
  ## colors so the plots look good
  comparison_df$mape_color <- "Empirical"
  comparison_df$tmapes_color <- "Theoretical"
  
  
  return(comparison_df)
}
