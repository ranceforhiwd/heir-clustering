# heir-clustering
Hierarchical Clustering

Our theory is to exploit the metadata we have regarding all the words and physical locations of the words inside documents. We are attempting to use clustering to group words that are in closely positioned on the page.  These groups are then used as attributes to give context for what the words or characters may be related to. Example, a complete address has a specific vocabulary about it using words such as "street, road, or route". There is also a particular grammar associated with those words and the way they are found to be grouped within the clusters provides clues on how to categorize the word.

This repository is using Python libraries and Docker containers to perform development and testing.

The main routine will search any document uploaded and scanned for text, if there is a valid US address, it will save the complete address in another database table.
