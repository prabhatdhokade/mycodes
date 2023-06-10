
// Prabhat Dhokade Tukaram

/*prime number
#include <iostream>

using namespace std;
int main(){
    int n;
    cin>>n;
    int n1;
    cin>>n1;
    int count =0;
    for(int i =n;i<= n1;i++){
        int flag = 1;
        for(int j =2;j<=i/2;j++){
            if(i%j == 0){
                flag =0;
                break;
            }
        }
        if(flag == 1) count++;
    }
    cout<< count;
}*/


/*factorial 

#include<bits/stdc++.h>
using namespace std;
int main() {
    long long n;
    cin>>n;
    long long i=1;
    long long sum =1;
    long long fact =1;
    while(i<=n){
        fact= fact*i;
        i++;
    }
    while(n>=1){
        sum =sum * n;
        n--;
    }
    cout<<fact<<" ";
    cout<< sum<<" ";
} 
*/
/*
fibonachi

#include<bits/stdc++.h>
using namespace std;

int fib(int n){
    if(n==0 || n==1) return n;
    return fib(n-1)+fib(n-2);
}

int main() {
    int n;
    cin>>n;
    int i=0;
    while(i<n){
    cout<<fib(i)<<" ";    
    i++; 
    }
}
*/
/*
#include<bits/stdc++.h>
using namespace std;

int fib(int n)
{
    int t[n+1];
    t[0] = 0;
    t[1] = 1;
    for(int i=0;i<n;i++){
        if(i==0 || i==1){
            cout<<t[i]<<" ";
        }
        else{ 
        t[i] = t[i-1]+t[i-2];
        cout<<t[i]<<" ";
        }
    }
    return t[n];
}


int main() {
    int n;
    cin>>n;
    fib(n);
}
*/
/*
#include<bits/stdc++.h>
using namespace std;

int fib(int n){
    if( n==0 || n==1){
        return n;
    }
    else{
        return fib(n-2) + fib(n-1);
    } 

}
int main(){
    int n;
    cin>>n;
    int i=0;
    while(i<n){
        cout<<fib(i)<<" ";
        i++;
    }
}
*/

/*
#include<bits/stdc++.h>
using namespace std;

int main(){
    int n;
    cin>>n;
    int a,b,c;
    a=0;
    b=1;
    cout<<a<<" "<<b<<" ";

    for(int i=2;i<n;i++){
        c = a + b;
        cout<<c<<" ";
        a = b;
        b = c;
    }
}  */

/* minimun elemnt in the array
#include<bits/stdc++.h>

using namespace std;
int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    int l =0;
    int s = -1;

    for(int i=0;i<n;i++){
        if(arr[i] > l ) l = arr[i];
    }
    cout<< l<<" ";

    for(int i=0;i<n;i++){
        if(arr[i] > s){
            if(arr[i] == l) continue;
            s= arr[i];
        }
    }
    cout<< s<<" ";

    int lr =arr[0];
    int sr =arr[1];
    if(arr[1] > arr[0]){
    lr =arr[1];
    sr =arr[0];
    }

    for(int i=2;i<n;i++){
        if(arr[i] > lr){
            sr = lr;
            lr = arr[i];
        }
        else if( arr[i] > sr){
            sr = arr[i];
        }
    }
    cout<<lr<<" " <<sr;
} 
*/
/*
#include<bits/stdc++.h>

using namespace std;

int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }

    for(int i=0;i<n;i++){
        if(arr[i] == 0 || arr[i] == 1){
            continue;
        }
        int flag = 0;
        for(int j=2;j<=arr[i]/2;j++){
            if(arr[i] % j == 0){
                flag = 1;
            }
        }
        if(flag == 0) {
            cout<<arr[i]<<" ";
        }
    }
}
*/
/* Armstrong number

#include<bits/stdc++.h>
using namespace std;

int main(){
    int n;
    cin>>n;
    int a;
    int b = n;
    int ans =0;
    int sum =0;
    while(n>0){
        int a = n % 10;
        sum += a * a * a;
        n = n /10;
    }
    if(sum == b) cout<<1;
    else cout<<0;
}
*/

/* square root 
#include<bits/stdc++.h>
using namespace std;

int main(){
    int n;
    cin>>n;
    int a = sqrt(n);
    if(a*a == n) cout<< 1;
    else cout<<0;
}
*/


/* palindrome
#include<bits/stdc++.h>
using namespace std;

int main()
{
    string s;
    cin>>s;
    int n=s.length(); 
    for(int i=0;i<n/2;i++){
        if(s[i] != s[n-1-i]){
            cout<<"false";
            break;
        }
        else 
            cout<<"true";
    }

}
*/
/*
#include<bits/stdc++.h>
using namespace std;

char * fact(int n){
    char a;
    int sum = 1;
    while(n>=1){
        sum = sum * n;
    } 
    cout<< sum;
    char* str =" ";
    return str;
}

int main(){
    int n;
    fact(n);
}
*/

/*

Duplicates in a string

#include<bits/stdc++.h>
using namespace std;
void solve(string s){
    map<char,int> mp;
    for(int i=0;i<s.size()-1;i++){
        mp[s[i]]++;
    } 
    for (auto i : mp)
        if(i.second > 1){
            cout<<i.first<<" ";
        }

}

int main(){
    string s;
    cin>>s;
    solve(s);
} */

/*  decimal to binary 

#include<bits/stdc++.h>
using namespace std;

void solve(int n){
    int i=1;
    int rem =1;
    int ans = 0;
    while(n>0){
        rem = n%2;
        n = n/2; 
        ans = ans + rem * i; // imp 
        i = i * 10; // imp
    }
    cout<<ans;
}

int main(){
    int n;
    cin>>n;
    solve(n);
}
*/

/* binary to decimal with integer

#include<bits/stdc++.h>
using namespace std;

int solve(int n){
    int rem=0;
    int ans=0;
    int i=0;
    while(n>0){
        rem = n % 10;
        n = n /10;
        ans = ans + rem * pow(2,i);
        i++;
    }
    return ans;
}

int main(){
    int n;
    cin>>n;
    cout<<solve(n);
}
*/

/* Binary to decimal using string

#include<bits/stdc++.h>
using namespace std;

int solve(string s){
    int ans =0;
    reverse(s.begin(),s.end());
    for(int i=0;i<s.size();i++){
        if(s[i] == '1'){
            ans += pow(2,i);
        }
    }
    return ans;
}

int main(){
    string s;
    cin>>s;
    cout<<solve(s);
}
*/

/* next same binary number with smae number of one's.

#include<bits/stdc++.h>
using namespace std;

int solve(int n){
     int i=1;
    int rem =1;
    int ans = 0;
    while(n>0){
        rem = n%2;
        n = n/2; 
        ans = ans + rem * i; // imp 
        i = i * 10; // imp
    }
    return ans;
}
int sum(int n){
    int ans=0;
    while(n>0){
        ans += n % 10;
        n = n /10;
    }
    return ans;
}
int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0;i<n;i++){
        cin>>arr[i];
    }
    for(int i=0;i<n;i++){
        int a = solve(arr[i]);
        int b =sum(a);
        for(int j=arr[i]+1;j<=100;j++){
            int c = solve(j);
            int d = sum(c);
            if(d == b){
                cout<<j<<" ";
                break;
            }
        }
    }
}
*/