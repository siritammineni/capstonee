import os
import shutil
import chardet
import difflib
import ftfy
import re
import html
from bs4 import BeautifulSoup
import numpy as np
import difflib
import hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


boilerplates=[ """Terms of Service | Web Terms of Service | Software License | Residential Services Policies | Report Abuse to Comcast | Terms for Feedback | Open Source Software | Purchased Content Terms and Conditions""",
"""Comcast © 2025. All rights reserved. The Xfinity Mobile logo and New Network mark (“O”) are the trademarks of Comcast Corporation or its subsidiaries."""]


def filter_access_denied_files(original_dir="data_selenium",new_dir="filtered_pages_selenium",access_denied_file="access_denied_urls.txt"):
   if not os.path.exists(new_dir):
       os.makedirs(new_dir)
   
   ACCESS_DENIED_TEXT = "Access Denied"
   
   access_denied_urls = []
   
   for file_name in os.listdir(original_dir):
       file_path = os.path.join(original_dir, file_name)
       
       if os.path.isfile(file_path):
           with open(file_path, "r", encoding="utf-8") as f:
               lines = f.readlines()
          
           if lines:
               url = lines[0].strip()  
               content = "".join(lines[1:])  
              
               if ACCESS_DENIED_TEXT in content:
                   print(f" Removing: {file_name}")
                   print(f"URL: {url}\n")
                   access_denied_urls.append(url)  
               else:
                   shutil.copy(file_path, os.path.join(new_dir, file_name))
  
   if access_denied_urls:
       with open(access_denied_file, "w", encoding="utf-8") as f:
           f.write("\n".join(access_denied_urls))
   print("\n Filtering completed! Clean files are in:", new_dir)
   print(f"Blocked URLs saved in: {access_denied_file}")


def filter_empty_content_files(original_dir="filtered_pages_selenium",new_dir="non_empty_pages_selenium",empty_content_file="empty-pagecontent.txt"):
  
   if not os.path.exists(new_dir):
       os.makedirs(new_dir)

   empty_content_urls = []
   
   for file_name in os.listdir(original_dir):
       file_path = os.path.join(original_dir, file_name)
       
       if os.path.isfile(file_path):
           with open(file_path, "r", encoding="utf-8") as f:
               lines = f.readlines()
           
           if lines:
               url = lines[0].strip() 
               content = "".join(lines[1:]).strip()  
               
               if not content:
                   print(f"Removing empty content file: {file_name}")
                   print(f" URL: {url}\n")
                   empty_content_urls.append(url)  
               else:

                   shutil.copy(file_path, os.path.join(new_dir, file_name))
  
   if empty_content_urls:
       with open(empty_content_file, "w", encoding="utf-8") as f:
           f.write("\n".join(empty_content_urls))
   print("\n Filtering completed! Non-empty files are in:", new_dir)
   print(f"Empty content URLs saved in: {empty_content_file}")


def find_unexpected_filenames(directory="non_empty_pages_selenium", prefix="https__www.xfinity.com_"):
   
   unexpected_files = []
   
   for file_name in os.listdir(directory):
       file_path = os.path.join(directory, file_name)
       
       if os.path.isfile(file_path):
           if not file_name.startswith(prefix):
               unexpected_files.append(file_name)

   if unexpected_files:
       print("\n Unexpected file names found:")
       for file in unexpected_files:
           print(f"    {file}")
   else:
       print("\n All files follow the expected naming pattern.")

def rename_filenames(directory="non_empty_pages_selenium", prefix="https__www.xfinity.com_"):
   
   for file_name in os.listdir(directory):
       file_path = os.path.join(directory, file_name)
       
       if os.path.isfile(file_path) and file_name.startswith(prefix):
           new_file_name = file_name[len(prefix):]  # Remove the prefix
           new_file_path = os.path.join(directory, new_file_name)
           
           os.rename(file_path, new_file_path)
           print(f"Renamed: {file_name} → {new_file_name}")
   print("\nRenaming completed! All files now have clean names.")   


def compare_file_contents(original_dir="non_empty_pages_selenium",
                         fixed_dir="utf8_fixed_pages_selenium"):
   
   modified_files = []
   for file_name in os.listdir(original_dir):
       original_path = os.path.join(original_dir, file_name)
       fixed_path = os.path.join(fixed_dir, file_name)
       
       if os.path.isfile(original_path) and os.path.isfile(fixed_path):
           with open(original_path, "r", encoding="utf-8", errors="ignore") as f1, \
                open(fixed_path, "r", encoding="utf-8", errors="ignore") as f2:
               original_content = f1.readlines()
               fixed_content = f2.readlines()
           
           if original_content != fixed_content:
               modified_files.append(file_name)
               print(f"\n Content changed in: {file_name}")
               diff = difflib.unified_diff(original_content, fixed_content,
                                           fromfile="Before UTF-8",
                                           tofile="After UTF-8",
                                           lineterm="")
               print("".join(diff))
   
   if not modified_files:
       print("\n No content changes found. UTF-8 conversion is safe.")
   else:
       print(f"\n {len(modified_files)} file(s) had content changes.")


def properly_fix_encoding(original_dir="non_empty_pages_selenium",
                         fixed_dir="utf8_fixed_pages_selenium"):
   
   
   os.makedirs(fixed_dir, exist_ok=True)
   for file_name in os.listdir(original_dir):
       original_path = os.path.join(original_dir, file_name)
       fixed_path = os.path.join(fixed_dir, file_name)
       
       if os.path.isfile(original_path) and file_name.endswith(".txt"):
           
           with open(original_path, "rb") as f:
               raw_data = f.read()
               result = chardet.detect(raw_data)
               detected_encoding = result["encoding"]
           
           if detected_encoding and detected_encoding.lower() != "utf-8":
               print(f"🔄 Fixing encoding for: {file_name} (Detected: {detected_encoding})")
               try:
                   
                   with open(original_path, "r", encoding=detected_encoding, errors="replace") as f:
                       content = f.read()
                   
                   fixed_content = ftfy.fix_text(content)
                
                   with open(fixed_path, "w", encoding="utf-8") as f:
                       f.write(fixed_content)
               except Exception as e:
                   print(f" Error fixing encoding for {file_name}: {e}")
           else:
               shutil.copy(original_path, fixed_path)
   print("\n Encoding fix completed! All files are now in:", fixed_dir)

# Define a whitelist of real HTML tags
htmltags_list = {
   "html", "head", "body", "title", "base", "link", "meta", "style", "header", "nav", "section",
   "article", "aside", "footer", "hgroup", "h1", "h2", "h3", "h4", "h5", "h6", "p", "hr", "pre",
   "blockquote", "b", "i", "strong", "em", "mark", "small", "del", "ins", "sub", "sup", "ul", "ol",
   "li", "dl", "dt", "dd", "table", "caption", "thead", "tbody", "tfoot", "tr", "th", "td", "colgroup",
   "col", "form", "input", "textarea", "button", "select", "option", "optgroup", "fieldset", "legend",
   "label", "datalist", "output", "details", "summary", "dialog", "menu", "menuitem", "img", "audio",
   "video", "source", "track", "embed", "object", "param", "iframe", "canvas", "svg", "math", "script",
   "noscript", "style", "template", "br", "wbr", "area", "map", "figure", "figcaption", "code", "samp",
   "kbd", "var", "abbr", "cite", "data", "time", "progress", "meter", "ruby", "rt", "rp", "bdi", "bdo", "span"
}
def extract_and_clean_html(text, filename, log_file):

   lines = text.split("\n")  
   if not lines:
       return None, text  
   first_line = lines[0] 
   content_lines = lines[1:]  
  
   remaining_text = "\n".join(content_lines)
   
   soup = BeautifulSoup(remaining_text, "html.parser")
  
   extracted_tags = []
   original_content = remaining_text  
   
   processed_text = str(soup)
   for tag in soup.find_all():
       tag_name = tag.name
       
       if tag_name in htmltags_list:
           extracted_tags.append(tag_name)
           processed_text = processed_text.replace(f"<{tag_name}>", "")
           processed_text = processed_text.replace(f"</{tag_name}>", "")
   extracted_tags_str = "\n".join(set(extracted_tags)) if extracted_tags else None
   
   clean_text = html.unescape(processed_text)
   
   cleaned_text = first_line + "\n" + clean_text if clean_text else first_line
   if extracted_tags:
       with open(log_file, "a", encoding="utf-8") as log_f:
           log_f.write(
               f" File: {filename}\n"
               f" Tags Removed: {extracted_tags_str}\n"
               f"{'-'*50}\n"
               f" Original Content:\n{original_content}\n"
               f"{'-'*50}\n"
               f"Cleaned Content:\n{cleaned_text}\n"
               f"{'='*50}\n\n"
           )
   return extracted_tags_str, cleaned_text

def clean_html_and_log(original_dir="utf8_fixed_pages_selenium", cleaned_dir="html_cleaned_pages", log_file="detected_html_tags.txt"):

   all_files = os.listdir(original_dir) 
   has_html = False  
   os.makedirs(cleaned_dir, exist_ok=True)
   count=0
   with open(log_file, "a", encoding="utf-8") as log_f:
       for file_name in all_files:
           original_path = os.path.join(original_dir, file_name)
           cleaned_path = os.path.join(cleaned_dir, file_name)
    
           if os.path.isfile(original_path) and file_name.endswith(".txt"):
               with open(original_path, "r", encoding="utf-8") as f:
                   content = f.read()
               
               extracted_tags, cleaned_content = extract_and_clean_html(content, file_name, log_file)
               if extracted_tags:
                   count+=1
                   has_html = True
                   
                   with open(cleaned_path, "w", encoding="utf-8") as f:
                       f.write(cleaned_content)
                   print(f" HTML tags removed in: {file_name}")
               else:
                   # Copy unmodified file as it is
                   shutil.copy(original_path, cleaned_path)
   if has_html:
       print("\n No of files with html tags : ", count)
       print(f"\n All files are now in: {cleaned_dir}")
       print(f" HTML content detected and appended to: {log_file}")
   else:
    
       shutil.rmtree(cleaned_dir)
       print(" No HTML tags found. Cleaned directory has been deleted.")

def clean_extra_spaces(text):

   lines = text.split("\n")
   if not lines:
       return text  
   first_line = lines[0]  
   content_lines = lines[1:]  
   cleaned_lines = [" ".join(line.split()) for line in content_lines]  # Splits by spaces & rejoins with single space
   cleaned_text = first_line + "\n" + "\n".join(cleaned_lines)
   cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text) 
   return cleaned_text

def clean_whitespace_in_files(original_dir="html_cleaned_pages", cleaned_dir="whitespace_cleaned_files"):

   all_files = os.listdir(original_dir)

   os.makedirs(cleaned_dir, exist_ok=True)
   for file_name in all_files:
       original_path = os.path.join(original_dir, file_name)
       cleaned_path = os.path.join(cleaned_dir, file_name)
       if os.path.isfile(original_path) and file_name.endswith(".txt"):
           with open(original_path, "r", encoding="utf-8") as f:
               content = f.read()
        
           cleaned_content = clean_extra_spaces(content)
           
           with open(cleaned_path, "w", encoding="utf-8") as f:
               f.write(cleaned_content)
           print(f" White space cleaned in: {file_name}")
   print(f"\n All files are now in: {cleaned_dir}")


def remove_boilerplate(text):
   lines = text.split("\n")
   if not lines:
       return text, False  
   first_line = lines[0]  
   content_lines = lines[1:]  
   
   filtered_lines = [line for line in content_lines if not any (bp in line for bp in boilerplates)]

   
   found_boilerplate = len(filtered_lines) < len(content_lines)
  
   cleaned_text = first_line + "\n" + "\n".join(filtered_lines)
   return cleaned_text, found_boilerplate

def clean_boilerplate_in_files(original_dir="whitespace_cleaned_files", cleaned_dir="boilerplate_processed_files"):
   
   count=0
   all_files = os.listdir(original_dir)

   os.makedirs(cleaned_dir, exist_ok=True)
   for file_name in all_files:
       original_path = os.path.join(original_dir, file_name)
       cleaned_path = os.path.join(cleaned_dir, file_name)
       if os.path.isfile(original_path) and file_name.endswith(".txt"):
           with open(original_path, "r", encoding="utf-8") as f:
               content = f.read()
    
           cleaned_content, found_boilerplate = remove_boilerplate(content)
           if found_boilerplate:
               count+=1
               print(f"Boilerplate removed from: {file_name}")
               with open(cleaned_path, "w", encoding="utf-8") as f:
                   f.write(cleaned_content)
           else:
               shutil.copy(original_path, cleaned_path)
   print("Number of files in which boilerplate was found: ", count)
   print(f"\n All files are now in: {cleaned_dir}")


def find_exact_duplicates(original_dir="boilerplate_processed_files", no_exact_dupes_dir="no_exact_duplicates", log_file="exact_duplicates_log.txt"):
   os.makedirs(no_exact_dupes_dir, exist_ok=True)
   file_hashes = {}
   duplicates = {}
   with open(log_file, "w", encoding="utf-8") as log_f:
       log_f.write("Exact Duplicate Files Log:\n\n")
       for file_name in os.listdir(original_dir):
           file_path = os.path.join(original_dir, file_name)
           if os.path.isfile(file_path) and file_name.endswith(".txt"):
               with open(file_path, "r", encoding="utf-8") as f:
                   lines = f.readlines()
                   content = "".join(lines[1:]).strip() if len(lines) > 1 else ""  # Ignore first line
              
               content = content.lower()
               content = re.sub(r"\s+", " ", content).strip()
               file_hash = hashlib.sha256(content.encode()).hexdigest()
               if file_hash in file_hashes:
                   duplicates.setdefault(file_hash, []).append(file_name)  
               else:
                   file_hashes[file_hash] = file_name  

       
       for file_name in os.listdir(original_dir):
           file_path = os.path.join(original_dir, file_name)
           destination_path = os.path.join(no_exact_dupes_dir, file_name)

           if os.path.isfile(file_path) and file_name.endswith(".txt"):
               file_hash = None
               with open(file_path, "r", encoding="utf-8") as f:
                   lines = f.readlines()
                   content = "".join(lines[1:]).strip() if len(lines) > 1 else ""
                   content = content.lower()
                   content = re.sub(r"\s+", " ", content).strip()
                   file_hash = hashlib.sha256(content.encode()).hexdigest()
               if file_hash and (file_name == file_hashes.get(file_hash) or file_hash not in duplicates):
                   shutil.copy(file_path, destination_path)  

       
       for file_hash, duplicate_files in duplicates.items():
           retained_file = file_hashes[file_hash] 
           log_f.write(f"Retained: {retained_file}\n")
           for dup in duplicate_files:
               log_f.write(f"Skipped: {dup}\n")
           log_f.write(f"{'-'*100}\n")
   print(f"\nExact duplicate filtering complete.")
   print(f"Retained + unique files copied to: {no_exact_dupes_dir}")
   print(f"Log saved in: {log_file}")


#filter_access_denied_files()


#filter_empty_content_files()


#find_unexpected_filenames()

#rename_filenames()

#properly_fix_encoding()


#compare_file_contents()


#clean_html_and_log()


#clean_whitespace_in_files()


clean_boilerplate_in_files()


find_exact_duplicates()
