# dirscanner
**Directory brute-force tool. Enumerates directory, checks for specific words in the content of the html and checks for possible directory traversal vulnerabilities**

![alt text](https://i.imgur.com/9oKBMBC.png)

## Overview
**dirscanner** is a simple tool written in Python that allows you to perform a directory brute-force enumeration in a website. It acts very similar to dirbuster but it has some extra functionalities:
  - For every website found it checks if the page has some confidential information by reading the HTML and searching for some specific words like "pass" or "password".
  - It also checks if the website is vulnerable to directory traversal attack by sending some basic requests.
  - Also **dirscanner** not only enumerates the different paths, it also checks for files with interesting extensions such as .txt, .php, .bak... similar to wfuzz program.
  
## Installation
  To install sqlifinder execute the following commands:
  
 `git clone https://github.com/roberreigada/dirscanner.git`
 
 `cd dirscanner`
 
 `sudo python3 setup.py install`
 
## How to use dirscanner?
Once it is installed you can run:
 
`dirscanner <URL> <wordlist>`
 
Example:
`dirscanner http://tabby/ /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt`