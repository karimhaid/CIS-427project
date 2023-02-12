//Original files created and tested by Erika to ensure connection
//Different than files provided by professor as those did not produce usable output

#include <stdio.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h> 


#define MAX 80
#define PORT 8080
#define SA struct sockaddr

//Erika-Added user structs for file and user information
struct Users{
int userID;
char first_name[50];
char last_name[50];
char user_name[50];
char password[50];
double usd_balance;
};
 
 
struct Stocks{
struct Users ID;
char stock_symbol[50];
char stock_name[50];
double stock_balance;
};
 

//Erika-Attempting to create function call for error checking in command statements
void checkValidBuy(void** userInput, int length){
for(int i = 0; i < length; i++){
if(isdigit(((char*) userInput[i])[0])){
printf("Element %d has INTEGER VALUE, required char maybe?\n", i *(int*) userInput[i]);
}
else if(userInput[i] == NULL){
printf("Element %d contains NULL value BAD INPUT\n", i);
}
else{
printf("Element is a string!: %s\n", i, (char*) userInput[i]);
}
}
}
 



//Erika- Function designed for chat between client and server for conditions for stocks
//Put Function calls, and info here, this continues on until specific terms are met so it ensures our server
//stays open
void func(int connfd)

{
//Erika-Created initial file checks for error checking
//File Check, check for server before writing more
//FILE *file;
//if(file = fopen("File.txt", "r")){
//fclose(file);
//printf("file exists\n");
//}
//else{
//printf("File doesn't exist\n");
//}
 
//Erika-Check if File with User data exists
FILE *usersFile;
char data[50];
 //Check if exists and print to screen for now for error checking
if(usersFile = fopen("UserFiles.txt", "r")){
fclose(usersFile);
printf("file exists\n");
}
 
//Erika-If Doesn't exist, so create it, have output and screenshots to ensure working properly
else{
usersFile = fopen("UserFiles.txt", "w");
 //Initial creation 
struct Users userData = {1, "Erika", "Baird", "airikuh", "1234", 100};
fwrite(&userData, sizeof(struct Users), 1, usersFile);
fclose(usersFile);
 //Read what was created for error checking
usersFile = fopen("UserFiles.txt", "r");
while(fread(&userData, sizeof(struct Users), 1, usersFile))
printf("%d %s %s %s %s %lf\n", userData.userID, userData.first_name,userData.last_name,userData.user_name,userData.password, userData.usd_balance);
fclose(usersFile);
 
}
 
 
    char buff[MAX];
    int n;
//Created array to copy buffer information into
char arrayCopy[MAX];

    // infinite loop for chat
    for (;;) {
        bzero(buff, MAX);
     
//Erika- Variable declarations and initializations to compare client input
//with commands
char buy[] = "BUY";
char sell[] = "SELL";
char list[] = "LIST";
char balance[] = "BALANCE";
char shutdown[] = "SHUTDOWN";
     
int k = 0;

        // read the message from client and copy it in buffer
        read(connfd, buff, sizeof(buff));

//Created by Erika & Jonathan to read buffer information into
char temp_strings[6 * 50];
        char words[6][50];
        int numWords = 0;
     //Copy buffer into created array
        memcpy(arrayCopy, buff, sizeof(buff));
        //char *p = strtok(trial_string, " ");
        //char *p = strtok(buff, " ");
        char *p = strtok(arrayCopy, " ");
     
     //Loop through array to get information
        while (p != NULL)
        {
            strcpy(words[numWords++], p);
         //Erika-Loop through to determine which words are integers and which 
         //are strings, output for error checking
         //attempted to move command input here but loops through each time
         //and can remove printed output instead of creating long loops for each
         //command
int is_integer = 1;
//Read in each array element pointed to by pointer
for(k; k < strlen(p); k++){
if(!isdigit(p[k])){
is_integer = 0;
break;
}
}
//If the pointer is an integer or string produce output for error checking
if(is_integer){
printf("%s is an integer\n", p);
            } else {
              printf("%s is a string\n", p);
           }
         //This was an error check by Erika to ensure output stopped if it encountered a specific 
         //input for later user input 
//else {
              //  printf("%s is a string, ERROR ERROR should have been an integer\n", p);
			//break;
            //}

            // Move to the next token
            p = strtok(NULL, " ");

}
        

        

//Created by Erika & Jonathan to ensure information printed to screen
        printf("ALL WORDS:\n");
        int i = 0;
        for (i; i < numWords; i++)
        {
            printf("%s\n", words[i]);
        }

     
//check if we can print words out here individually to do stuff with them
printf("Word 1: %s, Word 2: %s\n", words[0], words[1]);


        }


        // TRIAL !!!
 
 //Erika-Created command input loops to print to screen for now to ensure enters correct loop
 //Must be careful where these are placed or you encounter segmentation fault and alternate
 //parameter quantity
 if(strcmp(words[0], buy) == 0){
printf("Inside buy loop\n");
	 //Lets see if this works
	 checkValidInputBuy(words, numWords);
}


if(strcmp(words[0], sell) == 0){
printf("Inside sell loop\n");


}

if(strcmp(words[0], list) == 0){
printf("Inside list loop\n");


}

if(strcmp(words[0], balance) == 0){
printf("Inside balance loop\n");


}

if(strcmp(words[0], shutdown) == 0){
printf("Inside shutdown loop\n");


}





        // print buffer which contains the client contents
        printf("From client: %s\t To client : ", buff);


 
//ADDED TO COPY ARRAY for testing
memcpy(arrayCopy, buff, sizeof(buff));
 
 
         // print buffer which contains the client contents
printf("Array Copy buff check- %s...", buff);  
        bzero(buff, MAX);
        n = 0;
        // copy server message in the buffer
        while ((buff[n++] = getchar()) != '\n')
            ;

        // and send that buffer to client
        write(connfd, buff, sizeof(buff));

        // if msg contains "Exit" then server exit and chat ended.
        if (strncmp("exit", buff, 4) == 0) {
            printf("Server Exit...\n");
            break;

        }

    }

}





int main()

{

    int sockfd, connfd, len;

    struct sockaddr_in servaddr, cli;



    // socket create and verification

    sockfd = socket(AF_INET, SOCK_STREAM, 0);

    if (sockfd == -1) {

        printf("socket creation failed...\n");

        exit(0);

    }

    else

        printf("Socket successfully created..\n");

    bzero(&servaddr, sizeof(servaddr));



    // assign IP, PORT

    servaddr.sin_family = AF_INET;

    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);

    servaddr.sin_port = htons(PORT);



    // Binding newly created socket to given IP and verification

    if ((bind(sockfd, (SA*)&servaddr, sizeof(servaddr))) != 0) {

        printf("socket bind failed...\n");

        exit(0);

    }

    else

        printf("Socket successfully binded..\n");



    // Now server is ready to listen and verification

    if ((listen(sockfd, 5)) != 0) {

        printf("Listen failed...\n");

        exit(0);

    }

    else

        printf("Server listening..\n");

    len = sizeof(cli);



    // Accept the data packet from client and verification

    connfd = accept(sockfd, (SA*)&cli, &len);

    if (connfd < 0) {

        printf("server accept failed...\n");

        exit(0);

    }

    else

        printf("server accept the client...\n");



    // Function for chatting between client and server

    func(connfd);



    // After chatting close the socket

    close(sockfd);

}

  
