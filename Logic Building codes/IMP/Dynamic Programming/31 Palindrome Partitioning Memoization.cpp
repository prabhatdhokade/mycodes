#include<bits/stdc++.h>

using namespace std;

int static t[1001][1001];

bool ispallindrome(string s1,int i,int j) {   // check once for pallindrome code
    int n = s1.length();

    if(i == j) {
        return true; // single character is always a pallindome 
    }
    if(i > j) {
        return true; // empty string  is also a palindrome
    }
    while(i< j) {
        if(s1[i] != s1[j]) {
            return false;
        }
        i++;
        j--;
        
    }
    return true;
}


int solve(string s1,int i,int j) {

    if(i >= j) {     // if there is only one char in a string then how can we do partiion or in in a empty string
        return 0;
    }
    if (ispallindrome(s1,i,j) == true ) {   // check if it is a palindrome or not
        return 0;
    }
    if (t[i][j] != -1) { // memoization
        return t[i][j];
    }
    int min = INT_MAX;

    for(int k=i;k<j;k++) {  // remember the format 

        int temp = 1 + solve(s1,i,k) + solve(s1,k+1,j);  // 1 + beacuse we already did a partation

        if(temp < min) {
            min = temp;
        }      
    }
    t[i][j] = min;
    return min;
}

int mcm(string s1,int n) {
    int i=0;  // you have to think always can we set value of i =0 if yes proceed  
    int j = n-1; 
    memset(t,-1,sizeof(t));
    return solve(s1,i,j);
}


int main() {
    string s1;
    cin>>s1;
    int n = s1.length();
    cout<< mcm(s1,n);
}