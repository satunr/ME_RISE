import matplotlib.pyplot as plt
import numpy as np

# Example data (replace with your values) [WIKI-VOTE]
Y1 = [9.719110107421875, 28.586759958267212, 56.33913578033447, 5726.794832439423]          # Group 1 (e.g., Control)
Y1_err = [1.6100962293598047, 7.635045231912254, 15.571348323951284, 4037.2915748628493]
Y2 = [7.929169397354126, 22.030072994232178, 34.552188606262206, 117.44070499420167]      # Group 2 (e.g., Treatment)
Y2_err = [1.1437743287266768, 4.795905518728681, 10.074056441277323, 46.75022909387152]

# # Example data (replace with your values) [TWITTER]
# Y1 = [9.477247695922852, 21.84913370132446, 38.74652653694153, 508.6393807411194]          # Group 1 (e.g., Control)
# Y1_err = [1.6456934773361278, 3.7638641721000035, 8.323911777377011, 461.0682060550549]
# Y2 = [7.528621730804443, 16.333986291885378, 24.682994136810304, 67.81506050109863]          # Group 2 (e.g., Treatment)
# Y2_err = [1.5647648788527495, 2.76408508062283, 4.107051180090582, 12.679250232467302]


labels = ['100', '200', '300', 'Full']    # X-axis labels

# X positions and width
x = np.arange(len(labels))
width = 0.35  # width of the bars

# Create figure
plt.figure(figsize=(7, 5))

# Plot both bar groups with error bars
plt.bar(x - width/2, Y1, width, yerr=Y1_err, capsize=5,
        color='skyblue', edgecolor='black', label='Unscaled')
plt.bar(x + width/2, Y2, width, yerr=Y2_err, capsize=5,
        color='lightcoral', edgecolor='black', label='Scaled')

# Set log scale
plt.yscale('log')

# Labels and legend
plt.xticks(x, labels, fontsize=20)
plt.xlabel('Number of Nodes', fontsize=20)
plt.ylabel('Runtime in Seconds', fontsize=20)
plt.legend(fontsize=20)

plt.tight_layout()
plt.savefig('Runtime_Wiki.png', dpi=300)
plt.show()