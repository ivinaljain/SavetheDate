# SavetheDate
1. Inspiration I kept missing awesome UTD events, even though I’d snap pics of the posters in the hallway. I figured—why not turn those images into calendar events automatically?

What it does Save the Date! takes a picture of an event poster and converts it into an .ics calendar file, so you can easily add it to your calendar and never miss out.

How we built it We used OpenAI to extract event information from the poster images. Then, we formatted that info into a .ics file and even included a feature to send it via email.

Challenges we ran into The biggest challenge was converting the extracted JSON data into a proper .ics file format that plays nicely with all calendar apps.

Accomplishments that we're proud of Automating the flow from image to calendar file

Integrating OpenAI for smart text extraction

Getting the .ics format right for cross-platform compatibility

2. What we learned How .ics files work under the hood

Best practices for working with image-to-text models

Integrating different tools and APIs into a seamless workflow

3. What's next for Save the Date! Add OCR for handwritten posters

Build a mobile app version

Add automatic calendar syncing

Support batch uploads for multiple events at once
