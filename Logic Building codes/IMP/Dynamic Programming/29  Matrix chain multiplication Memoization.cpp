#include<bits/stdc++.h>
using namespace std;

// time complexity will be o(n^3);
// at line 21 or 22 t(k) * t(n-k) = o(n^2); that loop will runn n times so o(n^3) 


int static t[101][101];

int mcm(int arr[],int i,int j) {
    if(i>=j) {
        return 0;
    }

    if(t[i][j] != -1) {    // same as usaual if value is -1 then proceed if not then return  the saved value
        return t[i][j];
    }

    int min = INT_MAX;
    for(int k=i ;k<j ;k++) { // for k =i and k< j important
        int temp_ans = mcm(arr,i,k) + mcm(arr,k+1,j) + arr[i-1] * arr[k] * arr[j];

        if(temp_ans < min) {
            min = temp_ans;
        }
    }
    t[i][j] = min;
    return min;
}

int solve(int arr[],int n) {
    int i =1;
    int j =n-1;
    memset(t,-1,sizeof(t));  // memset set all value to -1 of matrix
    return mcm(arr,i,j);
}

int main() {
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++) {
        cin>>arr[i];
    }
    cout<<solve(arr,n);
}