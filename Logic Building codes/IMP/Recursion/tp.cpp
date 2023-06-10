#include<iostream>

using namespace std;

int main()
{
    /*string s ="Pr ab";
    cin>> s;

    for(int i=0; i< s.size(); i++) {
        if(i == 0){
            cout<<s[i];
        }


        if (s[i] ==' ')
        {
            cout<<s[i- 1]<<" "<< s[i+1];
        }
        
        if( i == s.length()-1) {
            cout<<s[i];
        }
    }
 */
    int n;
    cin>>n;
    int arr[n];
    for(int i =0; i<n;i++) {
        cin>>arr[i];
    } 
    int max =0;
    for(int i=n-1; i >= 0 ;i--) {
        if (arr[i] > max) {
            cout<< arr[i] <<" ";
            max = arr[i];
        }
    }
}