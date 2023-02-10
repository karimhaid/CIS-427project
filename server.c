#include <stdio.h>

#include <netdb.h>

#include <netinet/in.h>

#include <stdlib.h>

#include <string.h>

#include <sys/socket.h>

#include <sys/types.h>

#include <unistd.h> // read(), write(), close()





#define MAX 80

#define PORT 8080

#define SA struct sockaddr


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
 
 




// Function designed for chat between client and server for conditions for stocks

//Put Function calls, and info here, this continues on until specific terms are met so it ensures our server

//stays open

void func(int connfd)

{

//File Check, check for server before writing more
//FILE *file;
//if(file = fopen("File.txt", "r")){
//fclose(file);
//printf("file exists\n");
//}
//else{
//printf("File doesn't exist\n");
//}
 
//Check if File with User data exists
FILE *usersFile;
char data[50];
 //Check if exists and print to screen for now for error checking
if(usersFile = fopen("UserFiles.txt", "r")){
fclose(usersFile);
printf("file exists\n");
}
 
//If Doesn't exist, so create it
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

char arrayCopy[MAX];

    // infinite loop for chat

    for (;;) {

        bzero(buff, MAX);



        // read the message from client and copy it in buffer

        read(connfd, buff, sizeof(buff));


char temp_strings[6 * 50];
        char words[6][50];


        int numWords = 0;
        memcpy(arrayCopy, buff, sizeof(buff));
        //char *p = strtok(trial_string, " ");
        //char *p = strtok(buff, " ");
        char *p = strtok(arrayCopy, " ");
        while (p != NULL)
        {
            strcpy(words[numWords++], p);
            p = strtok(NULL, " ");
        }


        printf("ALL WORDS:\n");
        int i = 0;
        for (i; i < numWords; i++)
        {
            printf("%s\n", words[i]);
        }
        // TRIAL !!!



        // print buffer which contains the client contents

        printf("From client: %s\t To client : ", buff);


 
//ADDED TO COPY ARRAY for testing
memcpy(arrayCopy, buff, sizeof(buff));
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

  
