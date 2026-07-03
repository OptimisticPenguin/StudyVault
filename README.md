# STUDY GUIDE DATABASE BY JADEN VIBBERTS
#### Video Demo:  <[URL HERE](https://youtu.be/LQZUzdCR3p8)>
#### Description:

My project is designed to be a study guide database, as my goal is to help students in high school share various study guides in order to better improve their academics. This idea came about from one of my friends who would constantly share a link to a quizlet or google doc in a discord server in preparation for tests, and I thought it would be nice for it all to be in one place without needing to send various google drive links. This way, anyone studying for a subject would be able to see study guides for that unit. Since the only major standardized curriculums in the US at the high school level reside in AP courses, that is what my project would specifically target.

My project works by using the same login, register, apology and logout functions as the finance problem set, and uses a SQLite database with the tables of users (to store usernames and hash them), classes (to store the classes for various notes), and notes, where the bulk of the data is stored, containing keys to the other, as well as file_paths and thumbnail_paths.

Layout.html simply provides the navbar at the top.

Index.html provides a rows of pdf previews in columns of three, along with a filter function that allows a user to filter by class, which works by a SQL call of WHERE class of the pdf meets the selected class in between lines of SQL. That was probably one of the more interesting things I learned, how to add a portion of SQL between lines of SQL. A pagination bar prevents a single page from getting laggy and flooded with dozens of pdfs. Index.html is the main user of jinja loops in order to populate the screen with pdfs and pages.

Upload.html allows users to enter a title, a class from a dropdown menu, and upload a file to submit, which upload_success.html then links them back to the homepage.

Pdf-view.html allows for viewing the pdf, which includes a deletion button if you were the one who originally uploaded the pdf. It also includes a generate quiz button, which uses the chatGPT api as well as a text selected from pdfs in order to create a quiz based on the concepts in the pdf through AJAX updating the page without reloading it.

These html pages all carry most of the workload in this project, but they all interact with the backend, app.py which performs SQL calls in order to add, remove, and display items (pdfs and thumbnails) from the database. It uses GET and POST routes as well in order to render templates and gain information from forms like the upload function.

The largest challenge was handling the thumbnail upload and displaying it along with the pdf. Originally I wanted to use the pdf2image library in order to create a thumbnail image based off the first page of the pdf, but I had issues with actually installing it because it said it depended on poppler, which depended on homebrew in the terminal. It’s possible this was just a cs50 codespace interaction issue with certain libraries, but I’m not too sure. Later I switched to fitz in order to get this to work. I chose to implement a thumbnail so there would be a bit more color on the screen as well as people can see a preview of what they will get when they click on it. My goal was to emulate the homepage of google docs (except in dark mode).

The second part of this was debugging why the name of the class and the title wasn’t being passed to pdf_view.html correctly, and if I remember correctly, it was because of a quote function in the upload route that was changing the way spaces were handled in the database, where it was changing it to percent signs instead. This was especially tricky to troubleshoot because it was difficult to find where the problem was coming from because I had already written all of the code for the upload function by the time I was working on pdf-view.html.

The second largest challenge was managing the OpenAI API, because of the constant updates and outdated guides online about which function to actually call, and the logistics of working with the OpenAI key.

The third largest challenge was centering a div (the pagination bar) while having the filter dropdown bar aligned to the left. Even though there was no actual coding logic here, the issue lied in how the pagination div was being centered within the div that was already shifted to the right because of the dropdown button. I spent half a day working on this alone, and I ended up not being able to figure out how to center a div while interacting with another one on the same row/horizontal plane, so I opted to put the pagination bar at the bottom to get around this issue.

Credit to both UIverse for providing the button and the loading icon and the combination of the cs50 duck and GPT for helping me to learn AJAX and jinja syntax

In the end, I accomplished what I set out to do, but if I had more time in the future, I would implement a search function similar to Professor Malan’s example with the shows search function in week 9 where the page automatically updates when input is typed in, as well as a favorite/save system on certain pdfs so people can revisit the pdfs they visit most often without needing to search through the pages or filtering.

A big thanks to the cs50 team for this wonderful course!
