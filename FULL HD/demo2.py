import pyhtml

import Minh_page_1
import Minh_page_2
import Minh_page_3

import Long_page_1
import Long_page_2
import Long_page_3

pyhtml.need_debugging_help=True

#All pages that you want on the site need to be added as below
pyhtml.MyRequestHandler.pages["/"]=Minh_page_1; 
pyhtml.MyRequestHandler.pages["/Minh_page_2"]=Minh_page_2; 
pyhtml.MyRequestHandler.pages["/Minh_page_3"]=Minh_page_3; 

pyhtml.MyRequestHandler.pages["/Long_page_1"]=Long_page_1;
pyhtml.MyRequestHandler.pages["/Long_page_2"]=Long_page_2;
pyhtml.MyRequestHandler.pages["/Long_page_3"]=Long_page_3;
#Host the site!
pyhtml.host_site()