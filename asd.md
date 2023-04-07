I am making a technical write-up and I need you to score it and give me pointers on what i can improve.
# Crafting Robust Minecraft Backup Tools: A Deep Dive into ChunkVault-Lite and Teller-CLI## Preamble
Now I do not use the words “proof of concept” lightly here, every piece of code I wrote was to see If I could build an easy to deploy world backup tool that just works, I focused on real-world testing and developed primarily in a production environment (more on that in Why Deta Space and its Limitations) which led to some difficult decisions and some “over thought” solutions which in turn led me down the path of turning a few day project into a couple weeks of tinkering.## 1. Introduction
In the Minecraft community players invest countless hours building in and exploring virtual worlds. The unique creations and progress within these Minecraft worlds hold value to these players. The real world can be cruel sometimes, issues like data corruption, server issues and device migration lead to the loss of the precious memories. As someone who has lived this life and has seen it all from corrupted drives to lost usb’s I’ve dealt with my fair share of lost worlds that meant a lot to me, which led me to develop ChunkVault-Lite and Teller-CLI as proof of concept tools for a Minecraft world backup system.
ChunkVault-Lite serves as a frontend and backend application running in Deta Space that allows users to view their worlds and their respective backups (snapshots). Teller-CLI is a command-line tool that facilitates uploading and downloading worlds, ensuring compatibility with the backend by chunking files before uploading and reassembling them after download. Together, these tools provide the user with a simple to use Minecraft world backup system.
In this article, I will delve into the nitty-gritty of ChunkVault-Lite and Teller-CLI, exploring the challenges imposed by Deta Space, and demonstrate how to setup and use these tools effectively.## 2. Overview of the System Architecture### 2.1. ChunkVault-Lite
ChunkVault-Lite is the web application that serves both the frontend and backend of the backup system. The frontend provides the user a simple to use interface for viewing, editing, downloading and deleting worlds, while the backend handles storage, retrieval and serving of the world data. ChunkVault-Lite also provides a simple world sharing system that provides the latest backup (snapshot) to the public via a share link.### 2.2. Teller-CLI
Teller-CLI is the command-line interface tool that was designed specifically to interface with ChunkVault-Lite. It enables users to upload their Minecraft worlds to be backed-up, to download privately owned worlds or worlds shared through public URL’s from other users.### 2.3. Interaction
ChunkVault-Lite serves as the web application for managing backups (snapshots), while Teller-CLI is the command-line tool for uploading and downloading world backups (snapshots). Both are necessary in order to have a complete Minecraft world backup system.## 3. The Application (Frontend & Backend)
ChunkVault-Lite runs entirely in Deta Space using their micro’s (servers) and their Spacefile’s to instruct how they are run together. The way Deta Space runs micro’s using a proxy allows the frontend to run under the regular domain and the backend to run under `/api` allowing the frontend to make “local” fetch requests to the desired `/api` route.
Here is a stripped down example of the Spacefile, showing how the frontend is setup to be primary micro and the backend is set to live under the path `api`:
### 3.1. Frontend
The frontend of ChunkVault-Lite is designed to be an easy-to-use interface for users to interface with their Minecraft worlds and backups. It was built using SvelteKit with DaisyUI along with a custom Neubrutalism styling.#### Features
1. World overview: A list view of all uploaded Minecraft worlds, with thumbnails and world details, such as world name, difficulty and seed.
2. Backup management: Users can view the available backups (snapshots) for each world, with the option to download, or delete them.
3. Sharing option: The ability to generate a shareable link for specific worlds (this uses the most recent snapshot as a downloadable)
4. Simple editing: Users can change the info that shows up for other users when the world is accessed via the website (this does not change the actual worlds contents)
Figure 1: A screenshot of the main worlds screen for the ChunkVault-Lite Frontend showing the list view and world options.
Figure 2: A screenshot of a single world screen for the ChunkVault-Lite Frontend showing the world info an options as well as the worlds backups (snapshots)
Figure 3: A screenshot showing the edit window for a world in the ChunkVault-Lite frontend.### 3.2. Backend
The backend of ChunkVault-Lite is responsible for handling storage, retrieval and management of Minecraft worlds and their relevant backups. It was built using Python and FastAPI along with the Deta SDK.#### Features
1. World storage: Securely storing the uploaded Minecraft worlds and their respective backups in Deta Drive.
2. Backup management: Handling requests for backup creation, deletion and editing.
3. World serving: Serving the worlds and backups for download either through the frontend or via Teller-CLI.
4. API: Providing a well-documented API for anyone to build their own tools using it.## 4. The CLI Tool
Teller-CLI is a command-line tool designed to complement ChunkVault-Lite by providing an efficient way to upload and download Minecraft worlds. It is built using Python with Typer and HTTPx and is compatible with various platforms, including Windows, macOS, and Linux.
Key features and functionalities of Teller-CLI include:### 4.1. Uploading Worlds
Teller-CLI allows users to upload their Minecraft worlds to the ChunkVault-Lite backend by:
1. Pre-chunking the world files: To address Deta.space limitations, Teller-CLI splits the world files into smaller chunks before uploading. This process ensures the backend can handle the file sizes and minimizes the workload on the server.
2. Authenticating with the ChunkVault-Lite backend: Users must provide their API key to establish a secure and authorized connection with the backend.
3. Uploading the chunked world files: Teller-CLI uploads the chunks to the backend, where they are stored and managed by ChunkVault-Lite.
Figure 4: A flowchart showing the upload process for the API and how Teller-CLI communicates with the ChunkVault-Lite API### 4.2. Downloading Worlds
Teller-CLI enables users to download Minecraft worlds from their own backend or from a publicly shared URL provided by another user. The process involves:
1. Authenticating with the ChunkVault-Lite backend (if necessary): Users must provide their API key to access their own worlds or enter the shared URL for public worlds.
2. Downloading the chunked world files: Teller-CLI retrieves the chunked world files from the backend.
3. Reassembling the chunks: After downloading, Teller-CLI reassembles the chunks to recreate the original Minecraft world files.
Figure 5: A flowchart showing the download process for the API and how Teller-CLI communicates with the ChunkVault-Lite API depending on if the world is owned by the user or if its a shared URL. ## 5. Why Deta Space and its Limitations### 5.1. How it Started
When coming up with the idea of an easy-to-use Minecraft backup tool, I wanted something that everyone could use - something that was almost a one-button click and done. That’s where I landed on Deta Space.
Deta has been valuable in the development world for several years, offering a convenient way for developers to set up free project hosting. The recent transition to Deta Space as a platform introduced numerous improvements to the way applications can be built. Among these enhancements were essential features, such as a built-in proxy, credential & token authentication, and easy app installations. These changes made Deta Space the ideal platform for building our concept backup system.### 5,2. My Findings  During my research, I found out the hard way that this migration from the old Deta platform to the Deta Space platform was not without its hiccups. While the Deta team has made significant efforts to improve the platform, some limitations have persisted, creating challenges for developers to overcome. However, these challenges were making it difficult to verify the information I had, as it was primarily based on the documentation of the old platform, which might have been similar but could also have undergone upgrades and breaking changes that are yet to be added to the new documentation which was still in early stages while creating the systems.### 5.3. The Limitations
1. **250MB of Memory:** The working application and all data have to fall under 250MB, or else the application will fail to run.
2. **10s TTL:** Every request has a 10s Time To Live, meaning complex tasks cannot exceed this limit.
3. **10GB of Drive space:** The drive limit, at least from what I remember from the old platform, was 10GB per account, so I only take into account the full 10GB.
4. **6MB File Size:** When receiving a file request or sending a file request, 6MB was the max size.
5. **Python <= 3.9:** Not a deal-breaker, but made me go back to my older ways of developing FastAPI backends.
6. **Minecraft world size:** This was the biggest hurdle, which still plagues the lite version and always will. In my testing, simple world generation of a couple of hundred blocks adds about 10MB, give or take, every time.
7. **No True Dev Environment:** Deta space had no dev environment for use during creating of ChunkVault-Lite, recently `space dev` was added to the space cli which made iteration much faster.### 5.4. Overcoming Deta Limitations
The limitations posed significant challenges for a project with the primary objective of storing large compressed Minecraft world files.
The 10s TTL and 6MB File Size, on the other hand, were bigger concerns. One, sending a file meant it had to be smaller than 6MB, and two, 10s means that if the world was significant in size, the backend would not be able to chunk a file itself. Thus, Teller-CLI was created to chunk and upload the compressed world file (see Figure 4), as well as download the chunks and reassemble them into a playable world (see Figure 5).
The way the chunks are stored on the server is pretty straightforward; they follow this format:
```python
f"{snapshot_id}/{snapshot_name}.part{part_number}"
# l1qc7v4coo58/1680756146-snapshot.part1
```
Each part corresponds to a chunk of a .zip file. Meaning any “client” that requests the file parts from the server, must rebuild the .zip file from the raw bytes responded back by the server. Teller-CLI handles this for both public and private world backups, and ChunkVault-Lite’s frontend allows for downloading, because of the chunk system the download process is slow.
## 6. Installation and Setup
### ChunkVault-Lite
#### Installation
Installing ChunkVault-Lite is relatively simple, although setting it up for use with Teller-CLI can be a bit more challenging.
You can find ChunkVault-Lite on the Deta Space Discovery Page by searching for “ChunkVault” or by clicking  [Here](http://valink.io/) . Once the application is installed to your Canvas, follow the steps illustrated in the screenshots below, with the button locations highlighted in red.
Remember to save the generated API key for future access and store it securely:
Figure 6: A screenshot showing the freshly installed ChunkVault-Lite instance on the Deta Space Canvas, and where to click.
Figure 7: A screenshot showing to click the settings button on ChunkVault in the canvas.
Figure 8: A screenshot showing to click into the keys tab, then to click the “Create new API key” button.
Figure 9: A screenshot showing the API generation screen, showing the creating of an API key called “teller-cli”.
Figure 10: A screenshot showing where it shows the API key after generation and which button to click to copy the code.### Teller-CLI#### Installation
Installing Teller-CLI is straightforward, provided you have Python and pip installed. Simply enter the following command:
```bash
pip install teller-cli
```
This command enables the use of teller-cli in the terminal. When you first use Teller-CLI commands, you’ll be prompted to enter a base API URL, an API token for access through Deta’s authentication system (refer to Figures 6-10), and a default saves path for the Minecraft installation. The saves path must be the exact location of the saves folder within the main Minecraft folder. On Windows, this is usually `%appdata%/.minecraft` saves, while on Mac/Linux, it’s typically `~/.minecraft/saves`. These paths are default settings for their respective systems.
Figure 11:  A screenshot showing the flow for configuring teller-cli.## 7. Usage
Once ChunkVault-Lite is setup and Teller-CLI is configured to connect correctly to the backend using the API key, you are now able to upload and download worlds using the various commands, which you can become more aquatinted with by using the following command:
```bash
teller-cli --help
```
Figure 12: A screenshot showing the usage of `teller-cli --help` and what is returne### Uploading
Uploading is simple as teller-cli will take either a folder name of a world or the absolute path of a world, compresses it and uploads it to the ChunkVault-Lite backend.
```bash
teller-cli upload "New World"
teller-cli upload "/absolute/path/to/New World"
```
Figure 13: A screenshot showing the entire teller-cli upload process.### Downloading
Downloading is simple it takes either a snapshot ID or an entire share URL to a publicly shared world, allows the user to replace the world if the replace option is passed (otherwise, it creates a copy), allows you to save the compressed version of the world if need be, permits saving the compressed version of the world if needed, and allows changing the save location if you don’t want it saved at the default location.
```bash
teller-cli download l1qc7v4coo58 --replace
teller-cli download l1qc7v4coo58 --save "/Volumes/Backups/mc_saves"
teller-cli download "https://chunkvault-lite.jakepixl.dev/public/worlds/71C0S7E54DXAUYTRXJLDM"
```### Browsing
Browsing allows you to list your worlds in your terminal and download a specific snapshot, it also allows for replacing worlds, and changing the save path.
```bash
teller-cli browse
teller-cli browse --replace
teller-cli browse --save "/Volumes/Backups/mc_saves"
```## 8. Future Improvements and Contributions
The future of ChunkVault-Lite and Teller-CLI primarily revolves around essential fixes. As this was a proof of concept, the focus will remain on offering a straightforward method to back up Minecraft worlds, without much expansion. Instead, our attention will shift towards developing a more comprehensive, real-world solution with faster uploads/downloads, local and cloud storage options, enhanced clients, and more.
Rust 🦀 will play a vital role in the future development of ChunkVault. You might wonder why ChunkVault-Lite and Teller-CLI weren’t initially built using Rust; the reason is the limited Rust support in Deta Space at the time of the project’s inception.
ChunkVault-Lite is open-source, and we intend to maintain that openness for ChunkVault. This approach allows the Minecraft community to verify the safety of the application and encourages contributions from people with diverse backgrounds. Ultimately, our aim is to make ChunkVault the premier solution for preserving your cherished Minecraft creations.## 9. Conclusion
In summary, ChunkVault-Lite and Teller-CLI create a simple yet effective system for backing up and managing Minecraft worlds. This proof of concept has demonstrated the effectiveness and potential of a Minecraft backup tool. As the project transitions to a Rust-based ecosystem, I expect to see the performance increase significantly, more robust storage options, and overall improved user experiences.
I remain committed to keeping ChunkVault open-source, ensuring the safety and security of the users of ChunkVault as well as fostering collaboration within the Minecraft developer community.
Thank you for taking your time to read this write up, and Thank you for your interest in ChunkVault-Lite and Teller-CLI, I hope you can join us on the journey.