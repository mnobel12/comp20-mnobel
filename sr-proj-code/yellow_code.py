def analysis(datum):
#was here before culture show (adjusting analysis funciton to do the
    #averaging stuff for plot_array, and then you may have to change the
    #plot drawing function so that it doesn't redraw until every 5
    if(len(RAW_Q)%frequency == 0):
        sample_avg = np.mean(RAW_Q[-frequency:])
        PLOT_ARRAY.append(sample_avg)
