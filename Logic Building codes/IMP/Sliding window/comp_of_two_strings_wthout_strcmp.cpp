#include<iostream>
#include<stdio.h>
#include<string.h>

using namespace std;

int comp_str(char[],char[]);

int main()
{
    int flag;
    char a[25],b[25];

    //cout<<"Enter the first string";
    cin>>a;
    //cout<<"Enter the second string";
    cin>>b;

    flag=comp_str(a,b);
    if(flag==0)
    {
        cout<<1;

    }
    else
    {
        cout<<0;
    }
}

int comp_str(char a[],char b[])
{
     int i=0;
    while(a[i]==b[i])
    {
        if(a[i]=='\0'||b[i]=='\0')
         break;
        i++;
    }
    if (a[i]=='\0'&&b[i]=='\0')
        return 0;
    else
        return 1;
    
}


